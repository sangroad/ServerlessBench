// pass parameter when executing action. --param key value format

// function getTime() {
// 	return Date.now();
// }

// function getRandomInt(min, max) {
// 	return Math.floor(Math.random() * (max - min)) + min;
// }

// // time scale: ms
// function alu(time) {
// 	let one_base = 10000;
// 	let iter = 3 * time;
// 	let hrStart = process.hrtime();

// 	for (let i = 0; i < iter; i++) {

// 		for (let j = 0; j < one_base; j++) {

// 		}
// 	}
// 	let hrEnd = process.hrtime();
// 	let stTime = hrStart[0] * 1000000 + hrStart[1] / 1000
// 	let edTime = hrEnd[0] * 1000000 + hrEnd[1] / 1000

// 	console.log(edTime - stTime);	// in us
// }

function main(params) {
	// execTime = params.execTime
	let time = 50;
	let one_base = 35000;
	let iter = 1 * time;
	let hrStart = process.hrtime();

	for (let i = 0; i < iter; i++) {
		for (let j = 0; j < one_base; j++) {

		}
	}
	let hrEnd = process.hrtime();
	let stTime = hrStart[0] * 1000000 + hrStart[1] / 1000
	let edTime = hrEnd[0] * 1000000 + hrEnd[1] / 1000

	console.log((edTime - stTime)/1000);	// in us

	// let hrEnd = process.hrtime();
	// let edTime = hrEnd[0] * 1000000 + hrEnd[1] / 1000
	// console.log(edTime - stTime);	// in us

	// return { execTime: execTime, type: typeof(execTime) };
}
main()
