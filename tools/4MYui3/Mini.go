// 4MYui3
package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

func hook(path string, fInfo os.FileInfo, err error) error {
	if !fInfo.IsDir() {
		file_name_ext := filepath.Ext(path)
		if file_name_ext == ".js" && strings.Index(path, "-min.js") == -1 {
			println("Remove: " + path)
			os.Remove(path)
		}
	}
	return nil
}

func walk_dirs(path string) {
	err := filepath.Walk(path, hook)
	if err != nil {
		fmt.Printf("filepath.Walk() returned %v\n", err)
	}
}

func main() {
	flag.Parse()
	params_ := flag.Args()
	if len(params_) > 0 {
		root := flag.Arg(0)
		walk_dirs(root)
	}
}
