def calculate_stats(results_file_name):
    file = open(results_file_name, 'r+')
    file_content = file.read()
    file.seek(0, 0)
    line_num = 1
    solved_problems = 0
    total_problems = 0
    for line in file:
        if line_num > 1:
            solved = line[line.rfind(',') + 1:line.rfind('\\')]
            if solved.upper() == 'TRUE':
                solved_problems += 1
            total_problems += 1
        line_num += 1
    file.seek(0, 0)
    write_string = "Total_Problems: {},Solved_Problems: {}, Percentage_Solved: {}\n".format(total_problems, solved_problems, (solved_problems / total_problems) * 100)
    file.write(write_string + file_content)
    print(write_string)
    file.close()


if __name__ == "__main__":
    # calculate_stats('Hamming-Distance-seen-states-results.csv')
    calculate_stats('Hamming-Distance-results.csv')
