# Simple Python script for basic benchmarking of Ollama LLMs with MultipleChoice Q&A

## Overview

This repository contains a simple Python script designed to perform basica benchmarking on Ollama LLMs using a set of multiple-choice questions and answers. The goal of this script is to provide a basic yet effective way to measure the performance of different LLMs and quantisiations.

## Files in This Repository

- `runTest.py`: The main script that executes the benchmarking process.
- `MMLU_QandA.json`: A JSON file containing multiple-choice questions and answers used for testing.
- `License.txt`: The MIT license file.

## Prerequisites

Ensure you have the following software installed:
- Python 3.x

The script was only used and tested under Windows 11 and might require adjustments to be run under Linux or OSX.

## Usage

To run the benchmarking script, use the following command:
python runTest.py
The script will load the questions from MMLU_QandA.json and execute the benchmarking process, outputting the results to the console.

Be aware that the script only accepts single letter responses and otherwise rerequests the response. 
To avoid getting caught in infiinite loops with smaller models adjust the ensure_single_character_response function accordingly. 

## Customization
If you want to use a different set of questions, simply replace the MMLU_QandA.json file with your own JSON file following the same structure.
For use with other APIs adjust call_api function.

## Contributing
 - Fork the repository<br>
 - Create a new branch (git checkout -b feature-branch)<br>
 - Make your changes<br>
 - Commit your changes (git commit -am 'Add new feature')<br>
 - Push to the branch (git push origin feature-branch)<br>
 - Create a new Pull Request

## License
This project is licensed under the MIT License - see the License.txt file for details.

## Contact
For any inquiries, please contact Marco Thies at thies"at"consultt.net