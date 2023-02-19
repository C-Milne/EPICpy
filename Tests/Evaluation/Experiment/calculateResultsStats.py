import re
import math


def calculate_stats(results_file_name):
    file = open(results_file_name, 'r+')
    file_content = file.read()
    file.seek(0, 0)
    line_num = 1
    solved_problems = 0
    total_problems = 0
    domains = {}

    for line in file:
        if line_num > 1:
            solved = line[line.rfind(',') + 1:line.rfind('\\')]
            problem_domain = line[:line.find('/')]
            if solved.upper() == 'TRUE':
                solved_problems += 1
                commas = [m.start() for m in re.finditer(',', line)]
                solve_time = float(line[commas[1] + 1:commas[2]])
                if solve_time < 1:
                    problem_score = 1
                else:
                    problem_score = min(1, 1 - (math.log(solve_time) / math.log(1800)))
            else:
                problem_score = 0

            if problem_domain not in domains.keys():
                domains[problem_domain] = []
            domains[problem_domain].append(problem_score)
            total_problems += 1
        line_num += 1

    file.seek(0, 0)
    overview_string = "Total_Problems: {},Solved_Problems: {}, Percentage_Solved: {}\n".format(total_problems, solved_problems, (solved_problems / total_problems) * 100)

    total_score = 0
    domain_score_string = ""
    for domain in domains.keys():
        total_score += sum(domains[domain])
        domain_score_string += "{} ({}): {}\n".format(domain, len(domains[domain]), sum(domains[domain]))

    domain_score_string += "Total Score: {}\n".format(total_score)

    file.write(overview_string + domain_score_string + file_content)
    print(overview_string)
    file.close()


if __name__ == "__main__":
    calculate_stats('Hamming-Distance-seen-states-results.csv')
    calculate_stats('Hamming-Distance-results.csv')
    calculate_stats('Novelty_Facts_Only_Task-Method-Expand-0-results.csv')
    calculate_stats('Novelty-results.csv')
    calculate_stats('seen-state-breadth-first-results.csv')
    calculate_stats('Tree-Distance-seen-states-results.csv')
