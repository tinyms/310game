package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

func main() {
	req, _ := http.NewRequest("GET", "http://www.500.com/", nil)
	req.Header.Set("Connection", "close")
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		panic(err)
	} else {
		html, _ := ioutil.ReadAll(resp.Body)
		ioutil.WriteFile("a.htm", html, os.ModeAppend)
		fmt.Printf("%s", html)
	}
	fmt.Println("Resp code", resp.StatusCode)
	resp.Body.Close()
}
