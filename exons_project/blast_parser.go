package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"sync"
	"flag"

	"bytes"
)

var (
	parentPath string
	queryID    = regexp.MustCompile(`Query=\s+([^\s].+)`)
	CompInfo   = regexp.MustCompile(`(comp[^\s]+)\s*len=(\d*).+(\d[e.][^\n]+)`)
	contigData = make(map[string]string)
	compliment = map[string]string{"A":"T","T":"A","G":"C","C":"G"}
)

type blast struct {
	TaxaName string  `json:"taxa_name"`
	QueryID  string  `json:"query_id"`
	CompID   string  `json:"comp_id"`
	Length   int     `json:"length"`
	EValue   float64 `json:"e_value"`
	Reverse  bool    `json:"reverse"` //Strand=Plus/Minus
}

type blasts []blast

func (slice blasts) Len() int {
	return len(slice)
}

func (slice blasts) Less(i, j int) bool {
	return slice[i].EValue < slice[j].EValue
}

func (slice blasts) Swap(i, j int) {
	slice[i], slice[j] = slice[j], slice[i]
}

// getFileNames can be used to get the files that are in the blast folder or the contigs
func getFileNames(parentFolder string) (fileNames []string) {
	files, err := ioutil.ReadDir(parentFolder)
	if err != nil {
		log.Fatal(err)
	}
	parentPath = parentFolder + "/"
	for _, f := range files {
		// adding an additional filter just in case of OS junk
		if strings.Contains(f.Name(), ".fasta") {
			fileNames = append(fileNames, path.Join(parentFolder, f.Name()))
		}

	}
	return
}

//  isReversed quickly find the line Strand=Plus/Minus if found the strand is reversed
func isReversed(file, compID string) bool {
	b, err := ioutil.ReadFile(file)
	if err != nil {
		log.Fatal(err)
	}
	contents := string(b)
	start := strings.Index(contents, fmt.Sprintf("> %s", compID))

	if start == -1 {
		return false
	}

	end := strings.Index(contents[start:], "Query")
	end = end + start

	var chunk string
	if end < len(contents) && start < len(contents) {
		chunk = contents[start:end]
	}

	if strings.Contains(chunk, "Plus/Minus") {
		return true
	}
	return false
}

// readBlastFile reads the blast fasta.blast file, next time it might be easier to
// use the blast xml files as they are easier to parse
func readBlastFile(file string, wg *sync.WaitGroup, mtx *sync.Mutex, rawData chan []blast) {
	defer wg.Done()
	f, err := os.Open(file)
	if err != nil {
		log.Fatal(err)
	}
	defer f.Close()

	var data []blast
	scanner := bufio.NewScanner(f)

	for scanner.Scan() {
		// get the query if and if its a match start the next steps in the parser
		m := queryID.FindStringSubmatch(scanner.Text())
		if len(m) > 0 {
			var b blast
			// keep track of the taxa for contig matching later
			b.TaxaName = strings.Replace(strings.Split(file, ".")[0], parentPath, "", -1)
			b.QueryID = m[1]
			for scanner.Scan() {
				m = CompInfo.FindStringSubmatch(scanner.Text())

				if len(m) > 0 {
					length, err := strconv.Atoi(m[2])
					if err != nil {
						log.Fatal(err)
					}
					evalue, err := strconv.ParseFloat(m[3], 64)
					b.CompID = m[1]

					b.Length = length
					b.EValue = evalue
					b.Reverse = isReversed(file, b.CompID)
					// not sure if mutex is really needed here, but it couldn"t hurt in this case
					mtx.Lock()
					data = append(data, b)
					mtx.Unlock()
				} else {

					// if its the start of sequence of nothing was found denoted by the * then we got everything
					// start with the query ID again
					if strings.Contains(scanner.Text(), ">") || strings.Contains(scanner.Text(), "*") {
						break
					}
				}
			}
		}

	}
	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}

	rawData <- data
}

// loadContigData takes the data, normalizes it and stores everything in memory... might be an issue for larger datasets
func loadContigData(file, taxa string, mtx *sync.Mutex, wg *sync.WaitGroup) {
	defer wg.Done()
	b, err := ioutil.ReadFile(file)
	if err != nil {
		log.Fatal(err)
	}
	chunks := strings.Split(string(b), ">")
	for _, chunk := range chunks {
		lines := strings.Split(chunk, "\n")
		mtx.Lock()
		key := fmt.Sprintf("%s_%s", taxa, strings.Split(lines[0], " ")[0])
		contigData[key] = strings.Join(lines[1:], "\n")
		mtx.Unlock()
	}
}


//  inSlice checks to see if an item is already present in a slice
func inSlice(target blast, query []blast) bool {
	for _, q := range query {
		if q == target {
			return true
		}
	}
	return false
}

//  filterBlast for those OG matches that have one then one, we only want to best. So filter out...
func filterBlast(d []blast) []blast {
	var new []blast
	for _, b := range d {
		id := b.QueryID

		// get a tmp list
		var tmp blasts
		for _, b := range d {
			if b.QueryID == id {
				tmp = append(tmp, b)
			}
		}

		// sort by lowest e-value
		sort.Sort(tmp)
		var target blast
		if len(tmp) == 1 {
			if !inSlice(tmp[0], new) {
				new = append(new, tmp[0])
			}

		} else if len(tmp) > 1 {
			target = tmp[0]
			for _, b := range tmp {
				if b.EValue > target.EValue {
					break
				}
				if b.Length > target.Length {
					target = b
				}
			}
			if !inSlice(tmp[0], new) {
				new = append(new, target)
			}

		}

	}

	return new
}

//  removeDups ... ensure there is no duplicate data
func removeDups(d []blast) []blast {
	var new []blast
	for _, b := range d {
		if !inSlice(b, new) {
			new = append(new, b)
		}
	}
	return new
}

// reverse used to flip the dna string
func reverse(s string) string {
	chars := []rune(s)
	for i, j := 0, len(chars)-1; i < j; i, j = i+1, j-1 {
		chars[i], chars[j] = chars[j], chars[i]
	}
	return string(chars)
}

// splitSubN using it to normalize length
func splitSubN(s string, n int) []string {
	sub := ""
	subs := []string{}

	runes := bytes.Runes([]byte(s))
	l := len(runes)
	for i, r := range runes {
		sub = sub + string(r)
		if (i + 1) % n == 0 {
			subs = append(subs, sub)
			sub = ""
		} else if (i + 1) == l {
			subs = append(subs, sub)
		}
	}

	return subs
}

func main() {

	blastFolder := flag.String("blasts", "/Users/marcsantiago/Desktop/exon/BLASTs", "Path to the blast folders")
	contigFolder := flag.String("contigs", "/Users/marcsantiago/Desktop/exon/contigs", "Path to the contigs folders")
	outputFolder := flag.String("unique", "output", "Create an output folder in the working directory")
	flag.Parse()


	files := getFileNames(*blastFolder)
	rawData := make(chan []blast)
	var wg sync.WaitGroup
	mtx := &sync.Mutex{}
	// fan out method of parsing the data
	var taxa []string
	for _, file := range files {
		wg.Add(1)
		taxa = append(taxa, strings.Replace(strings.Split(file, ".")[0], parentPath, "", -1))
		go readBlastFile(file, &wg, mtx, rawData)
	}

	go func() {
		wg.Wait()
		close(rawData)
	}()

	data := []blast{}
	for d := range rawData {
		filtered := filterBlast(d)
		clean := removeDups(filtered)
		// flatten the data into a single slice
		for _, c := range clean {
			data = append(data, c)
		}

	}
	// inline sort slower... but i have a definition above already (go 1.8 and up)
	sort.Slice(data, func(i, j int) bool {
		return data[i].QueryID < data[j].QueryID
	})

	// get all the file paths from the contigs folder
	files = getFileNames(*contigFolder)
	// load config information into a global map
	for i, file := range files {
		wg.Add(1)
		go loadContigData(file, taxa[i], mtx, &wg)

	}
	wg.Wait()

	// make the output folder
	if _, err := os.Stat(*outputFolder); os.IsNotExist(err) {
		os.Mkdir(*outputFolder, 0777)
	}

	var buf bytes.Buffer
	currentID := data[0].QueryID
	for i, d := range data {

		var sequence string
		if s, ok := contigData[d.TaxaName+"_"+d.CompID]; ok {
			sequence = s
		}
		if d.Reverse{
			// complement dna
			var tmp string
			for _, seq := range sequence {

				if v, ok := compliment[string(seq)]; ok {
					tmp += v
				} else {
					tmp += string(seq)
				}
			}
			// reverse the sequence
			sequence = strings.Join(splitSubN(strings.Replace(reverse(tmp), "\n", "", -1), 60), "\n") + "\n"

		}
		buf.WriteString(fmt.Sprintf(">%s\n", d.TaxaName))
		buf.WriteString(sequence)
		
		// get the future value, one step ahead
		j := i + 1
		if j < len(data) {
			if currentID != data[j].QueryID {
				err := ioutil.WriteFile(path.Join(*outputFolder, currentID+".fasta"), buf.Bytes(), 0644)
				if err != nil {
					panic(err)
				}
				currentID = data[j].QueryID
				buf.Reset()
			}
		}
	}
}
