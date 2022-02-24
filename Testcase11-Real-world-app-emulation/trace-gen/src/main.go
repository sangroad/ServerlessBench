package main
import "fmt"
import "time"

func loop(count int) {
	for i := 0; i < count; i++ {
		for j := 0; j < 2650000; j++ {

		}
	}
}

func fine_loop(count int) {
	for i := 0; i < count; i++ {
		for j := 0; j < 2650000; j++ {

		}
	}
}

// Main function for the action
func Main(obj map[string]interface{}) map[string]interface{} {
	/*
	name, ok := obj["name"].(string)
	if !ok {
		name = "world"
	}
	fmt.Printf("name=%s\n", name)
	msg := make(map[string]interface{})
	msg["single-main"] = "Hello, " + name + "!"
	*/
	arg_time := obj["time"].(int)
	//int_time, _ := strconv.Atoi(arg_time)
	start := time.Now()

	fine_loop(arg_time)
	//fine_loop(arg_time)
	//fine_loop(arg_time)

	elapsed := time.Since(start)
	//fmt.Println(elapsed.Nanoseconds())
	//fmt.Println(elapsed.Microseconds())
	//fmt.Println(elapsed.Milliseconds())
	fmt.Println(elapsed)

	msg := make(map[string]interface{})
	msg["single-main"] = "Hello, hyosang!"
	return msg
}

func main() {
	hyo := make(map[string]interface{})
	//hyo["name"] = "hyosang"
	hyo["time"] = 15	// in millisecond
	Main(hyo)
}
