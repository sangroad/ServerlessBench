#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <chrono>
#include <vector>
#include <sstream>
#include <future>
#include <thread>
#include <cstdlib>
#include <cerrno>
#include <cstring>
using namespace std;
using clock_type = std::chrono::high_resolution_clock;

// key: app name, value: number of app activation
map<string, int> activ_cnt;

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

int run_workload(string timeline_path, const string res_file) {
	ifstream timeline_file(timeline_path);
	string line;
	string prev_res;
	vector<int> run_idx;
	map<int, string> app_idx = parse_app_order(timeline_path);
	unsigned int inv_cnt = 0;
	int while_iter = 0;
	vector<FILE*> sh_arr;

	if (!timeline_file.is_open()) {
		return -1;
	}

	for (const auto &item : app_idx) {
		activ_cnt[item.second] = 0;
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

			for (int idx : run_idx) {
				string tmp_app_name = app_idx[idx];
				cmd = "wsk -i action invoke " + tmp_app_name + " > " + res_file;
				sh = popen(cmd.c_str(), "r");
				activ_cnt[tmp_app_name]++;
				// printf("cmd: %s\n", cmd.c_str());
				if (sh == NULL) {
					printf("err number: %d, errr str: %s\n", errno, strerror(errno));
				}
				sh_arr.push_back(sh);
				// cmd += "wsk -i action invoke app" + to_string(idx) + " > " + res_file + ";";
			}
			inv_cnt++;

			if (inv_cnt % 30 == 0) {
				auto end_time = clock_type::now();
				printf("duration: %ld\n", chrono::duration_cast<chrono::microseconds>(end_time - start_time).count());
			}

			if (inv_cnt % 50 == 0) {
				ifstream temp_file(res_file);
				string temp_str;
				getline(temp_file, temp_str);
				if (prev_res == temp_str) {
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
			}

		}

		this_thread::sleep_until(target_time);
		// prev_time = clock_type::now();
		// printf("while duration: %ld\n", chrono::duration_cast<chrono::microseconds>(prev_time - start_time).count());
	}

	printf("workload end!\n");
	// printf("total app invocations: %d\n", inv_cnt);

	string cmd = "wsk -i action invoke func-------";
	popen(cmd.c_str(), "r");

	return inv_cnt;
}

void print_total_invocation(string path, int64_t duration) {
	string app_compute_info = path + "/appandIATMap.csv";
	map<string, int> functions_per_app;
	ifstream file(app_compute_info);
	string line;
	int total_activations = 0;

	getline(file, line);

	while (getline(file, line)) {
		vector<string> tmp = split(line, ',');
		string appName = tmp[0];
		int funcs_cnt = stoi(tmp[3]);
		functions_per_app[appName] = funcs_cnt;
	}

	for (const auto &item : activ_cnt) {
		int tmp = item.second * functions_per_app[item.first];
		printf("app: %s, functions for app: %d, app activations: %d, functions activations: %d\n", 
			item.first.c_str(), functions_per_app[item.first], item.second, tmp);
		total_activations += tmp;
	}

	double rps = total_activations / duration;
	printf("total function invocations: %d\n", total_activations);
	printf("rps: %lf\n", rps);
}

string move_success_workload(string workload_dir, string success_dir, string sample_num, string runtime) {
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
	string cmd = "cp -r " + workload_dir + " " + success_dir + new_dir;
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

void print_usage() {
	printf("./run_success <workload name to run>\n");
}

int main(int argc, char *argv[]) {

	if (argc == 1) {
		print_usage();
		return 0;
	}

	auto tmp = split(argv[1], '_');
	const string SAMPLE_NUM = tmp[0];
	const string RUNTIME = tmp[3];

	const string success_dir = "../CSVs/success/" + string(argv[1]);
	const string timeline_path = success_dir + "/funcTimeline_" + SAMPLE_NUM + ".csv";
	const string res_file = "req_response";
	const string pickme_data_path = "/home/caslab/workspace/PICKME/data";
	string success_path;

	auto start_time = clock_type::now();
	int ret = run_workload(timeline_path, res_file);
	auto end_time = clock_type::now();
	auto duration = chrono::duration_cast<chrono::seconds>(end_time - start_time).count();

	print_total_invocation(success_dir, duration);

	if (ret != -1) {
		write_success_workload_to_pickme(success_path, pickme_data_path);
	}

	printf("workload duration: %ld\n", duration);
	
	return 0;
}

