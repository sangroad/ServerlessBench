#include <iostream>
#include <fstream>
#include <string>
#include <yaml-cpp/yaml.h>
#include <chrono>
#include <vector>
#include <sstream>
#include <thread>
using namespace std;
using clock_type = std::chrono::high_resolution_clock;

vector<int> split(string input, string match, char delim) {
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

int run_workload(string timeline_path) {
	ios::sync_with_stdio(false);

	ifstream timeline_file(timeline_path);
	string line;
	string cmd;
	vector<int> run_idx;

	if (!timeline_file.is_open()) {
		return -1;
	}

	while(getline(timeline_file, line)) {
		auto start_time = clock_type::now();
		auto target_time = start_time + 1ms;

		if (line.find("1") != string::npos) {
			FILE *shell = NULL;
			run_idx = split(line, "1", ',');
			for (int idx : run_idx) {
				// cmd = "wsk -i action invoke app" + to_string(idx) + " &";
				cmd = "wsk -i action invoke app" + to_string(idx);
				shell = popen(cmd.c_str(), "r");
				cout << cmd << endl;
			}

			auto end_time = clock_type::now();
			// cout << chrono::duration_cast<chrono::microseconds>(end_time - start_time).count() << "us\n";
		}

		this_thread::sleep_until(target_time);
	}

	return 0;

}

int main() {
	YAML::Node config = YAML::LoadFile("config.yaml");
	const string SAMPLE_NUM = config["sample_number"].as<string>();
	const string workload_dir = "../CSVs/" + SAMPLE_NUM;
	const string timeline_path = workload_dir + "/funcTimeline_" + SAMPLE_NUM + ".csv";

	run_workload(timeline_path);

	// auto start_time = clock_type::now();

	// FILE *ls = popen("wsk -i action invoke app0", "r");

	// auto end_time = clock_type::now();
	// cout << chrono::duration_cast<chrono::microseconds>(end_time - start_time).count() << endl;

	// pclose(ls);
	
	return 0;
}