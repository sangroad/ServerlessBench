#include <iostream>
#include <fstream>
#include <string>
#include <yaml-cpp/yaml.h>
#include <chrono>
#include <vector>
#include <sstream>
#include <future>
#include <thread>
#include <cstdlib>
#include <cerrno>
#include <cstring>
#include <random>
#include <algorithm>
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

void clear_openfiles(vector<FILE*> *v) {
	for (auto item : *v) {
		pclose(item);
	}
	v->clear();
}

int run_rand_workload(string timeline_path, const string res_file) {
	ifstream timeline_file(timeline_path);
	string line;
	string prev_res;
	vector<int> run_idx;
	map<int, string> app_idx = parse_app_order(timeline_path);
	unsigned int inv_cnt = 0;
	int while_iter = 0;
	vector<FILE*> sh_arr;
	int func_first = 0;	// max: 130
	int func_second = 0;	// max: 999

	random_device rd[2];
	mt19937 gen[2] = {mt19937(rd[0]()), mt19937(rd[1]())};
	uniform_int_distribution<int> dis(0, 139);

	if (!timeline_file.is_open()) {
		return -1;
	}

	// auto prev_time = clock_type::now();
	printf("workload generation start!\n");

	while(getline(timeline_file, line)) {
		while_iter++;
		FILE *sh = NULL;
		auto start_time = clock_type::now();
		auto target_time = start_time + 1ms;

		if (line.find("1") != string::npos) {
			string cmd;
			run_idx = split_and_match(line, "1", ',');
			int size = run_idx.size();

			// execute random function. It is safe because all of functions have same runtime
			for (int i = 0; i < size; i++) {
				string temp = to_string(func_first);
				string first_id = string(3 - temp.length(), '0') + temp;

				temp = to_string(dis(gen[1]));
				// temp = to_string(func_second);
				string second_id = string(3 - temp.length(), '0') + temp;
				cmd = "wsk -i action invoke func" + first_id + "-" + second_id + " > " + res_file + " &";

				/*
				if (func_second == 299) {
					// func_first = (func_first + 1) % 131;
					func_second = (func_second + 1) % 300;	// func000-000 ~ func000-199
				}
				else {
					func_second++;
				}
				*/

				sh = popen(cmd.c_str(), "r");
				// printf("cmd: %s\n", cmd.c_str());
				if (sh == NULL) {
					printf("err number: %d, errr str: %s\n", errno, strerror(errno));
					return -1;
				}
				sh_arr.push_back(sh);
				inv_cnt++;
			}

			if (inv_cnt % 30 == 0) {
				auto end_time = clock_type::now();
				printf("duration: %ld\n", chrono::duration_cast<chrono::microseconds>(end_time - start_time).count());
			}

			if (inv_cnt % 100 == 0) {
				ifstream temp_file(res_file);
				string temp_str;
				getline(temp_file, temp_str);

				if (temp_str.find("error:") != string::npos) {
					printf("Openwhisk cannot invoke function!!\n Exit...\n");
					return -1;
				}
				else if (prev_res == temp_str) {
					printf("Delay on function execution!\n");
				}
				else {
					prev_res = temp_str;
				}
				auto end_time = clock_type::now();
				printf("After result file check duration: %ld\n", chrono::duration_cast<chrono::microseconds>(end_time - start_time).count());
			}

			if (inv_cnt % 200 == 0) {
				// close opened files asynchronously
				future<void> fut = async(launch::async, clear_openfiles, &sh_arr);
				auto end_time = clock_type::now();
				printf("After clear opened file duration: %ld\n", chrono::duration_cast<chrono::microseconds>(end_time - start_time).count());
				printf("Executed functions: %d\n", inv_cnt);
			}

		}

		this_thread::sleep_until(target_time);
	}

	printf("workload end!\n");

	string cmd = "wsk -i action invoke func-------";
	FILE* sh = popen(cmd.c_str(), "r");
	char tmp[10240];
	fgets(tmp, 10240, sh);

	if (string(tmp).find("error:") != string::npos) {
		printf("Openwhisk is now unavailable!\n");
		return -1;
	}

	return inv_cnt;
}

void print_total_invocation(string path, int64_t duration, int inv_cnt) {
	string app_compute_info = path + "/appandIATMap.csv";
	map<string, int> functions_per_app;
	ifstream file(app_compute_info);
	string line;
	int total_activations = inv_cnt;

	getline(file, line);

	while (getline(file, line)) {
		vector<string> tmp = split(line, ',');
		string appName = tmp[0];
		int funcs_cnt = stoi(tmp[3]);
		functions_per_app[appName] = funcs_cnt;
	}

	double rps = total_activations / duration;
	printf("total function invocations: %d\n", total_activations);
	printf("rps: %lf\n", rps);
}

string move_workload(string workload_dir, string target_dir, string sample_num, string runtime) {
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
	while (getline(app_info_file, line)) {
		func_cnt++;
	}
	app_info_file.close();

	// new dir: number of applicaitons + shortest IAT + number of functions + execution time
	string new_dir = sample_num + "_" + IAT + "_" + to_string(func_cnt) + "_" + runtime;
	string cmd = "cp -r " + workload_dir + " " + target_dir + new_dir;
	cout << cmd << endl;
	popen(cmd.c_str(), "r");

	return new_dir;
}

void write_success_workload_to_pickme(string success_path, string pickme_path) {
	string sshpass = "sshpass ssh caslab@10.150.21.198 ";
	string echo = "\"echo " + success_path + " > " + pickme_path + "/current_workload\"";
	string cmd = sshpass + echo;
	printf("cmd: %s\n", cmd.c_str());

	FILE *sh = popen(cmd.c_str(), "r");
	pclose(sh);

	printf("Writing current workload to pickme done\n");
}

int main(int argc, char *argv[]) {
	YAML::Node config = YAML::LoadFile("config.yaml");
	const string SAMPLE_NUM = config["sample_number"].as<string>();
	const string RUNTIME = config["total_run_time"].as<string>();
	const string workload_dir = "../CSVs/" + SAMPLE_NUM;
	const string success_dir = "../CSVs/success/";
	const string timeline_path = workload_dir + "/funcTimeline_" + SAMPLE_NUM + ".csv";
	const string res_file = "req_response";
	const string pickme_data_path = "/home/caslab/workspace/PICKME/data";

	auto start_time = clock_type::now();
	int ret = run_rand_workload(timeline_path, res_file);
	auto end_time = clock_type::now();
	auto duration = chrono::duration_cast<chrono::seconds>(end_time - start_time).count();

	// successful workload
	if (ret != -1) {
		print_total_invocation(workload_dir, duration, ret);
		string success_path = move_workload(workload_dir, success_dir, SAMPLE_NUM, RUNTIME);
		printf("%s\n", success_path.c_str());
		write_success_workload_to_pickme(success_path, pickme_data_path);
	}

	printf("workload duration: %ld\n", duration);

	return 0;
}