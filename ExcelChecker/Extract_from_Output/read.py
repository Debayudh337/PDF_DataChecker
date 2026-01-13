import re

def read(file_path):
    # Read the file content
    with open(file_path, 'r') as file:
        input_text = file.read()

    # Regular expression to extract name, UID, and marks
    name_pattern = r'Student Name:\s(.+)'  
    uid_pattern = r'UID:\s(\d+)'             
    marks_pattern = r'(\w+\s?\w*):\s(\d+)'   

   
    student_name = re.search(name_pattern, input_text).group(1)
    uid = re.search(uid_pattern, input_text).group(1)

    
    matches = re.findall(marks_pattern, input_text)

    # Print name and UID
    print(f'Student Name: {student_name}')
    print(f'UID: {uid}\n')

   
    marks_list = []

    
    for subject, mark in matches:
        print(f'{subject}: {mark}')
        marks_list.append(int(mark))

    
    marks_list = marks_list[1:]

    
    print("\nUpdated Marks List (after removing the first element):", marks_list)

