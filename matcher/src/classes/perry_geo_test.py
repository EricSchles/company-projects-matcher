import util
import initial_solution
import perry_geo_annealing as pg
import random_teams

import distance
import numpy as np
#input_file = "tests.csv"

class CompError(Exception):
	def __init__(self, value):
		self.val = value
	def __str__(self):
		return repr(self.val)

# Framework to use perrygeo's python-simulated-annealing library.

def random_solutions_and_goodness(use_file, students, feasible_projects, num_MBAs, num_MEngs, num_times = 100):
		'''
			Returns a list of projects.
		'''
		min_energy = float("inf")
		min_sol = None
		for i in range (0, num_times):
			init = initial_solution.make_initial_solution(students, feasible_projects, num_MBAs, num_MEngs)
		#	print "There are  " + str(len(feasible_projects)) + " feasible projects"
			print "Random solution " + str(i) + ":"
			for p in init:
				print str(p.ID) + ":" + str([s.ID for s in p.students])
			inv_cov_mat_tup = distance.create_inv_cov_mat_from_data(use_file, students)
			#inv_cov_mat = inv_cov_mat_tup[0]
			cur_energy = pg.energy((init, inv_cov_mat_tup))
			if (cur_energy < min_energy):
				min_sol = init
				min_energy = cur_energy
		for p in min_sol:
			print str(p.ID) + ":" + str([s.ID for s in p.students])
		print "The minimum energy is " + str(min_energy)
		return [p for p in min_sol if len(p.students) > 0]

def pick_disjoint_seeds(use_file, students, feasible_projects, num_MBAs, num_MEngs, num_times = 10):
		# Make an initial random solution.
		# Record the projects that are on that solution.
		# Make another random solution without any of those projects.
		# Pick "best and different."
		pass

def print_final_solution(state):
		print "Final Solution:"
 		(projects, inv_cov_mat_tup) = state
		for p in projects:
		 	print str(p.ID) + ": " + str([s.ID for s in p.students])
		 	print "Student attributes: " + str([s.get_numerical_student_properties()])
		 	print "Diversity: " + str(p.calculate_diversity(inv_cov_mat_tup))
			ranks = []
			# NOTE: get ranking returns 100 if the student did not rank the project.
		 	for student in p.students:
				rank = student.get_ranking(p.ID)
				print "rank"
				#cost = student.get_cost_from_ranking(rank)
				ranks.append(rank)
			avg_project_rank = np.mean(ranks)
			print "Average project rank: " + str(avg_project_rank)

def manual_schedule(use_file, students, sol, annealer):
 		#def create_inv_cov_mat_from_data(use_file, students, file = default_file):

		inv_cov_mat_tup = distance.create_inv_cov_mat_from_data(use_file, students)
		state = (sol, inv_cov_mat_tup)
		print "Initial energy is " + str(pg.energy(state))
		# Manually set the annealing schedule.
		state, e = annealer.anneal(state, 10000000, 0.01, 54000, updates=0)
		print_final_solution(state)

		print "Final energy is " + str(e)
		print "Calculated final energy is " + str(pg.energy(state))

		# def anneal(self, state, Tmax, Tmin, steps, updates=0):
  #       """Minimizes the energy of a system by simulated annealing.
        
  #       Keyword arguments:
  #       state -- an initial arrangement of the system
  #       Tmax -- maximum temperature (in units of energy)
  #       Tmin -- minimum temperature (must be greater than zero)
  #       steps -- the number of steps requested
  #       updates -- the number of updates to print during annealing
        
  #       Returns the best state and energy found."""

def make_random_students():
		remaining_num_MBAs = 37
 		remaining_num_MEngs = 35
 		MBAs = random_teams.create_random_MBAs(4, 4, remaining_num_MBAs)
 		MEngs = random_teams.create_random_MEngs(4, 4, remaining_num_MEngs)
 		students = MBAs + MEngs
		return students

def greedy_solutions_and_goodness(students, feasible_projects, num_times = 1000):
		'''
			Returns a list of projects.
		'''
		min_energy = float("inf")
		min_rank = float("inf")
		min_sol = None
		for i in range (0, num_times):
			#Reset the feasible projects.
			for project in feasible_projects:
				project.students = []
			
			init = initial_solution.greedy_initial_solution_and_fill_unmatched(students, feasible_projects)
			print "Greedy solution " + str(i) + ":"
			avgs = []
			def calculate_avg_rank(solution):
				for p in solution:
					print str(p.ID) + ":" + str([s.ID for s in p.students])
					print "Ranks:",
					rankings = [s.get_ranking(p.ID) for s in p.students]
					print rankings
					avg_rank = np.mean(rankings)
					print "Average rank: " + str(avg_rank)
					avgs.append(avg_rank)
				overall_average_rank = np.mean(avgs)
				return overall_average_rank
			cur_avg_rank = calculate_avg_rank(init)
			print "Overall average rank: " + str(cur_avg_rank)

			if (len(init) < 17):
				raise CompError("Not 17 projects.")

			# Actually calculating the energy.
			#	inv_cov_mat_tup = distance.create_inv_cov_mat_from_data(False, students)
			#cur_energy = pg.energy((init, inv_cov_mat_tup))
			#if (cur_energy < min_energy):
			#	min_sol = init
			#	min_energy = cur_energy

			# Just compare the average ranks.
			if (cur_avg_rank < min_rank):
				min_sol = init
				min_rank = cur_avg_rank


		# for p in min_sol:
		# 	print str(p.ID) + ":" + str([s.ID for s in p.students])
	#	print "The minimum energy is " + str(min_energy)
		print "The minimum overall avg rank is " + str(min_rank)
		min_sol_projects = [p for p in min_sol if len(p.students) > 0]
		print [p.ID for p in min_sol_projects]
		print "This solution has an overall avg rank of " + str(calculate_avg_rank(min_sol_projects))
		return min_sol_projects

def do_random_initial_solutions(students, all_projects, annealer):
 		feasible_projects = util.create_feasible_projects(students, all_projects, verbose = True)
	 	sol = random_solutions_and_goodness(False, students, feasible_projects, 37, 35, num_times = 100)
	 	print "About to do manual schedule"
	 	manual_schedule(False, students, sol, annealer)

def do_greedy_initial_solutions(students, all_projects, annealer, verbose = False):
		feasible_projects = util.create_feasible_projects(students, all_projects, verbose)
		sol = greedy_solutions_and_goodness(students, feasible_projects)
		print "finished greedy solutions and goodness. The solution we got is:"
		print [p.ID for p in sol]
		print "About to do manual schedule"
	# 	manual_schedule(False, students, sol, annealer)

def test_project_diversities(students, all_projects):
		project = util.random_project(all_projects, [], reuse = False)
		print "For project " + str(project.ID)
		for i in range(5):
			project.students.append(students[i])
			print (students[i].get_student_properties())
		print project.calculate_diversity()

		project_two = util.random_project(all_projects, [project], reuse = False)
		print "For project " + str(project_two.ID)
		for i in range(5, 10):
			project_two.students.append(students[i])
			print (students[i].get_student_properties())
		print project_two.calculate_diversity()	



