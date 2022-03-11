#include <iostream>
#include <fstream>
#include <string>
#include <yaml-cpp/yaml.h>
#include <chrono>
#include <vector>
#include <sstream>
#include <future>
#include <thread>
using namespace std;
using clock_type = std::chrono::high_resolution_clock;

vector<string> split(string input, char delim) {
	vector<string> result;
	stringstream ss(input);
	string temp;

	while(getline(ss, temp, delim)) {
		result.push_back(temp);
	}

	return result;
}

vector<int> split_and_match(string input, string match, char delim) {
	vector<int> result;
	stringstream ss(input);
	string temp;
	int cnt = 0;

	while(getline(ss, temp, delim)) {
		if (temp == match) {
			result.push_back(cnt);
		}
		cnt++;
	}

	return result;
}

int print_result(FILE* sh) {
	char line[10240];

	if (fgets(line, 10240, sh) != NULL) {
		printf("%s", line);
		return 1;
	}
	else {
		return 0;
	}
}

map<int, string> parse_app_order(string timeline_path) {
	ifstream file(timeline_path);

	// key: index of app in timeline csv file, value: app name
	map<int, string> res;
	int cnt = 0;
	string line;

	getline(file, line);
	vector<string> apps = split(line, ',');

	for (string app : apps) {
		res.insert({cnt, app});
		cnt++;
	}

	return res;
} 

int run_workload(string timeline_path, const string res_file) {
	ifstream timeline_file(timeline_path);
	string line;
	string prev_res;
	vector<int> run_idx;
	map<int, string> app_idx = parse_app_order(timeline_path);
	// std::future<int> fut;
	unsigned int inv_cnt = 0;
	int while_iter = 0;

	if (!timeline_file.is_open()) {
		return -1;
	}

	// auto prev_time = clock_type::now();
	printf("workload generation start!\n");

	while(getline(timeline_file, line)) {
		while_iter++;
		auto start_time = clock_type::now();
		auto target_time = start_time + 1ms;

		if (line.find("1") != string::npos) {
			// FILE *shell = NULL;
			string cmd = "";
			run_idx = split_and_match(line, "1", ',');

			for (int idx : run_idx) {
				cmd += "wsk -i action invoke " + app_idx[idx] + " > " + res_file + ";";
				// cmd += "wsk -i action invoke app" + to_string(idx) + " > " + res_file + ";";
			}
			popen(cmd.c_str(), "r");
			inv_cnt++;

			if (inv_cnt % 50 == 0) {
				ifstream temp_file(res_file);
				string temp_str;
				getline(temp_file, temp_str);
				if (prev_res == temp_str) {
					printf("There is an delay in function execution!\n");
					// return -1;
				}
				else {
					prev_res = temp_str;
					printf("%s\n", temp_str.c_str());
				}
			}
			// fut = std::async(std::launch::async, print_result, shell);

			// auto end_time = clock_type::now();
			// printf("duration: %ld\n", chrono::duration_cast<chrono::microseconds>(end_time - start_time).count());
		}

		this_thread::sleep_until(target_time);
		// prev_time = clock_type::now();
		// printf("while duration: %ld\n", chrono::duration_cast<chrono::microseconds>(prev_time - start_time).count());
	}

	printf("workload end!\n");
	printf("total while iterations: %d\n", inv_cnt);
	printf("total app invocations: %d\n", inv_cnt);

	string cmd = "wsk -i action invoke func-------";
	popen(cmd.c_str(), "r");

	return inv_cnt;

}

void move_success_workload(string workload_dir, string success_dir, string sample_num) {
	string map_file_path = workload_dir + "/appandIATMap.csv";
	ifstream map_file(map_file_path);
	string line;

	getline(map_file, line);
	getline(map_file, line);

	string IAT = split(line, ',')[1];
	map_file.close();

	string app_info_file_path = workload_dir + "/appComputeInfo.csv";
	ifstream app_info_file(app_info_file_path);

	int func_cnt = 0;
	while(getline(app_info_file, line)) {
		func_cnt++;
	}
	app_info_file.close();

	// new dir: number of applicaitons + shortest IAT + number of functions
	string new_dir = sample_num + "_" + IAT + "_" + to_string(func_cnt);
	string cmd = "cp -r " + workload_dir + " " + success_dir + new_dir;
	cout << cmd << endl;
	popen(cmd.c_str(), "r");
}

int main() {
	YAML::Node config = YAML::LoadFile("config.yaml");
	const string SAMPLE_NUM = config["sample_number"].as<string>();
	const string workload_dir = "../CSVs/" + SAMPLE_NUM;
	const string success_dir = "../CSVs/success/";
	const string timeline_path = workload_dir + "/funcTimeline_" + SAMPLE_NUM + ".csv";
	const string res_file = "req_response";

	parse_app_order(timeline_path);

	auto start_time = clock_type::now();
	int ret = run_workload(timeline_path, res_file);
	auto end_time = clock_type::now();

	if (ret != -1) {
		move_success_workload(workload_dir, success_dir, SAMPLE_NUM);
	}

	printf("workload duration: %ld\n", chrono::duration_cast<chrono::milliseconds>(end_time - start_time).count());
	
	return 0;
}