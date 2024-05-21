import json
from pathlib import Path
import subprocess
import time

# Initialize accumulators for summarizing response values
total_duration_sum = 0
load_duration_sum = 0
prompt_eval_count_sum = 0
prompt_eval_duration_sum = 0
eval_count_sum = 0
eval_duration_sum = 0

def read_json_file(file_path):
    try:
        # Attempt to open and read the JSON file
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None

def create_prompts(data, instruction, max_prompt_amount=None):
    # Create a list of formatted prompts based on the input data and instruction using "list comprehension"
    prompts = [
        # For each entry in the data, format the prompt string with the instruction and question
        f"{instruction}\nQuestion:\n{entry['question']}\n\nAnswer:"
        # Iterate over the data with an index using enumerate
        for i, entry in enumerate(data)
        # If max_prompt_amount is set (not None), include entries only up to the max_prompt_amount
        if not max_prompt_amount or i < max_prompt_amount
    ]
    # Return the list of formatted prompts
    return prompts

def call_api(prompt, user, password, ip, model, debug=False):
    global total_duration_sum, load_duration_sum, prompt_eval_count_sum, prompt_eval_duration_sum, eval_count_sum, eval_duration_sum

    url = f"https://{ip}/api/generate"
    data = {"model": model, 
            "prompt": prompt, 
            "stream": False,
            "options": {
                    "temperature": 0
            }
    }
    command = [
        "curl", "-k", "--user", f"{user}:{password}", url, 
        "-d", json.dumps(data), "-H", "Content-Type: application/json"
    ]
    
    if debug:
        print(f"Sending request to {url} with data: {data}")
    
    try:
        result = subprocess.run(command, capture_output=True, text=True)
        if debug:
            print("Command executed:", " ".join(command))
            print("Response received:", result.stdout)
        
        response_json = json.loads(result.stdout)
        # Save the first and last JSON response
        if 'first_response' not in globals():
            global first_response
            first_response = response_json
        global last_response
        last_response = response_json

        # Accumulate the values from the response JSON
        total_duration_sum += response_json.get("total_duration", 0)
        load_duration_sum += response_json.get("load_duration", 0)
        prompt_eval_count_sum += response_json.get("prompt_eval_count", 0)
        prompt_eval_duration_sum += response_json.get("prompt_eval_duration", 0)
        eval_count_sum += response_json.get("eval_count", 0)
        eval_duration_sum += response_json.get("eval_duration", 0)

        # Try to get the value associated with the key "response", if not found return "No response found"
        return response_json.get("response", "No response found").strip()
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f"Error during API call: {e}")
        return "Error in response"

def ensure_single_character_response(prompt, user, password, ip, model, debug=False):
    while True:
        response = call_api(prompt, user, password, ip, model, debug)
        if len(response) == 1:
            return response
        if debug:
            print("Response contains more than one character, requesting response again!")

def process_prompts(prompts, user, password, ip, model, num_runs, debug=False):
    # Initialize a list to store all responses for each prompt
    all_responses = [[] for _ in range(len(prompts))]
    # Iterate over the number of runs
    for _ in range(num_runs):
        # For each prompt, get a single character response and append it to the corresponding list
        for i, prompt in enumerate(prompts):
            response = ensure_single_character_response(prompt, user, password, ip, model, debug)
            all_responses[i].append(response)
    return all_responses

def analyze_responses_debug(predefined_answers, all_responses):
    wrong_response_count = []
    different_responses_count = []

    for predefined_answer, responses_in_prompt in zip(predefined_answers, all_responses):
        # Count how many responses don't match the predefined answer
        wrong_count = sum(1 for response in responses_in_prompt if response != predefined_answer)
        wrong_response_count.append(wrong_count)

        # Count the number of unique responses for one prompt
        unique_responses = len(set(responses_in_prompt))
        different_responses_count.append(unique_responses)
    # Return the counts of wrong answers and different responses
    return wrong_response_count, different_responses_count

def display_comparison_debug(data, all_responses, wrong_response_count, different_responses_count):
    # Define the header for the table
    header = ["Answer"] + [f"Resp.{i+1} " for i in range(len(all_responses[0]))] + ["Wrong Resp. count", "Different Resp. count"]
    # Print the header
    print("\t".join(header))
    print("=" * (10 * (len(header))))

    # For each entry, responses, wrong answer count, and different responses count, print the row
    for entry, responses, wrong_count, diff_count in zip(data, all_responses, wrong_response_count, different_responses_count):
        predefined_answer = entry.get("answer", "N/A").strip()
        response_row = [predefined_answer] + responses + [str(wrong_count), str(diff_count)]
        print("\t".join(response_row))

def analyze_responses(predefined_answers, all_responses):
    # Extract the first run responses
    responses = [responses[0] for responses in all_responses]
    # Count the matches between predefined answers and first run responses
    matches = sum(1 for predefined, response in zip(predefined_answers, responses) if predefined == response)
    total = len(predefined_answers)
    # Calculate the accuracy
    accuracy = (matches / total) * 100
    return responses, matches, accuracy

def display_comparison(predefined_answers, responses, matches, accuracy):
    # Print the header for predefined answers vs. first run responses
    print(f"{'Answer':<8}{'Responses':<10}")
    print("=" * 18)
    # Print each predefined answer and its corresponding first run response
    for predefined, response in zip(predefined_answers, responses):
        print(f"{predefined:<8}{response:<20}")
    # Print the total matches and accuracy
    print("\nResponse statistics:")
    print(f"  Total requests:   {len(predefined_answers)}")
    print(f"  Total Matches:    {matches}")
    print(f"  Accuracy:         {accuracy:.2f}%")

def print_inference_statistics(inference_time, first_response, last_response):

    print("\nInference statistics:")

    # Print the summarized values and first/last JSON responses
    print(f"\n  Total time for inference measured by script: {inference_time:.2f} seconds")
    
    # Print selected fields from first and last JSON respons
    print(f"  First JSON Response created_at:           {first_response.get('created_at', 'N/A')[:-8]}")
    print(f"  First JSON Response load_duration in ms:  {first_response.get('load_duration', 'N/A') / 1000000:.2f}")
    print(f"  Last JSON Response created_at:            {last_response.get('created_at', 'N/A')[:-8]}")
    print(f"  Last JSON Response load_duration in ms:   {last_response.get('load_duration', 'N/A') / 1000000:.2f}")

    # Calculate per token metrics
    prompt_eval_per_token = prompt_eval_duration_sum / prompt_eval_count_sum if prompt_eval_count_sum > 0 else 0
    eval_per_token = eval_duration_sum / eval_count_sum if eval_count_sum > 0 else 0

    # Print the summed values 
    print(f"\n  Metrics per API-Statistics in responses:")
    print(f"  Total Duration in ms:           {total_duration_sum / 1000000:.2f}")
    print(f"  Load Duration in ms:            {load_duration_sum / 1000000:.2f}")
    print(f"  Prompt Eval Count:              {prompt_eval_count_sum}")
    print(f"  Prompt Eval Duration in ms:     {prompt_eval_duration_sum / 1000000:.2f}")
    print(f"  Eval Count:                     {eval_count_sum}")
    print(f"  Eval Duration in ms:            {eval_duration_sum / 1000000:.2f}")
    print(f"  Prompt Token / s:               {1000 / (prompt_eval_per_token / 1000000):.2f}")
    print(f"  Eval Token / s:                 {1000 / (eval_per_token / 1000000):.2f}")

def main():
    ip = "10.0.0.1:8443"
    user = "user"
    password = "pw"
    model = "llama3:70b-instruct-q4_K_M"
    max_prompt_amount = 57
    debug = False
    num_runs = 5 if debug else 1

    instruction = ("Please respond with the correct letter (A, B, C or D) to the question. Do not give explanations! "
                   "Here is an example: \n'Question:\n What color does a ripe banana have?\n"
                   "(A) Blue\n(B) Green\n(C) Yellow\n(D) Red\n\nAnswer:C' \nRespond the correct letter to this Question:\n")

    script_dir = Path(__file__).parent
    json_file_path = script_dir / 'MMLU_QandA.json'

    # Step 1: Read the JSON file
    data = read_json_file(json_file_path)
    if data is None:
        return

    # Step 2: Create prompts
    prompts = create_prompts(data, instruction, max_prompt_amount)

    # Step 3: Process prompts and get responses from the API in form of all_responses[prompt_number][run_number]
    inference_start_time = time.time()  # Save start time of inference
    all_responses = process_prompts(prompts, user, password, ip, model, num_runs, debug)
    inference_time = time.time() - inference_start_time # Save time of inference

    if debug:
        # Step 4: Get data for output and analyze the responses
        data_slice = data[:max_prompt_amount] if max_prompt_amount else data
        predefined_answers = [entry.get("answer", "N/A").strip() for entry in data_slice]
        wrong_response_count, different_responses_count = analyze_responses_debug(predefined_answers, all_responses)

        # Step 5: Display the comparison of predefined answers, LLM responses, wrong answers
        display_comparison_debug(data_slice, all_responses, wrong_response_count, different_responses_count)
        print_inference_statistics(inference_time, first_response, last_response)

    else:
        # New Step 4 for non-debug mode
        data_slice = data[:max_prompt_amount] if max_prompt_amount else data
        predefined_answers = [entry.get("answer", "N/A").strip() for entry in data_slice]
        responses, matches, accuracy = analyze_responses(predefined_answers, all_responses)

        # New Step 5 for non-debug mode
        display_comparison(predefined_answers, responses, matches, accuracy)
        print_inference_statistics(inference_time, first_response, last_response)

if __name__ == "__main__":
    main()
