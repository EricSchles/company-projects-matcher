import numpy as np 
import pandas as pd 

import classes
import itertools
from classes import Student
from classes import Team
from classes import Project
from classes import CompError
from classes import FieldError

student_ids = []

# Just for the initial test case.
names_projects = {3705: 'Goldman Sachs',
				2990: 'American Express',
				4225: 'Google',
				2860: 'Facebook',
				2145: '500px',
				1820: 'FlightCar',
				3055: 'Flatiron',
				1040: 'Realize',
				1950: 'Shapeways',
				1625: 'charity:water',
				3445: 'Bonobos',
				3900: 'Bloomberg'}

# Normalize each element in a list by the list min and max.
def normalize_bet_zero_and_one(lst):
	lst_max = lst.max()
	lst_min = lst.min()
	den = lst_max - lst_min
	num = [elm - lst_min for elm in lst]
	# TODO: get rid of this stupid error.
	if (den == 0):
		raise CompError("In normalizing our quantitative variables, all values are the same.")
	final = [(elm * 1.0) / den for elm in num]
	return final

# For each of the IDs in classes' valid projects, create a project object with that ID.
# As a default, each project requires 2 MBAs and 2 MEngs.
def generate_all_projects(num_MBAs = 2, num_MEngs = 2):
	projects_lst = []
	for ID in classes.vals_valid_projects:
		p = Project(ID, num_MBAs, num_MEngs)
		projects_lst.append(p)
	return projects_lst

def get_project_from_ID(ID, projects):
	matching_ID_lst = filter(lambda x: x.ID == ID, projects)
	if (len(matching_ID_lst) == 0):
		error = "ID " + str(ID) + " does not match to a valid project."
		raise FieldError(error)
	elif (len(matching_ID_lst) > 1):
		error = "There is more than one matching project. Problem!"
		raise FieldError(error)
	
	# Otherwise, there is one element in the list and it matches our desired ID.
	else:
		return matching_ID_lst[0]

# Filter out projects with insufficient rankings to get matched.
# Returns a list of projects which passed the test.
def remove_infeasible_projects(students, projects, verbose = False):
	insufficient_IDs = []
	for p in projects:
		matched = filter(lambda x: p.ID in x.project_rankings, students)
		if (verbose):
			print "For project " + str(p.ID) + ":"
			print [s.ID for s in matched]
		MBAs_ranked = [s for s in matched if s.degree_pursuing == "MBA"]
		MEngs_ranked = [s for s in matched if s.degree_pursuing == "MEng"]
		if (verbose):
			print [s.ID for s in MBAs_ranked]
			print [s.ID for s in MEngs_ranked]

	 	if (len(MBAs_ranked) < p.num_MBAs or len(MEngs_ranked) < p.num_MEngs):
	 		if (verbose):
	 			string = "Not enough MBAs or MEngs ranked project "
	 			string += str(p.ID)
	 			string += " for it to be included."
	 			print string
	 		insufficient_IDs.append(p.ID)

	projects = filter(lambda p: not(p.ID in insufficient_IDs), projects)
	return projects

# For a specific project p, get the students' overall interest in the project.
# Higher interest means that more students ranked it highly on their lists.
def get_project_interest_from_rankings(p, students, verbose = False):

	# Check which students ranked this project.
	matched = filter(lambda s: p.ID in s.project_rankings, students)
	if (verbose):
		print "The following students ranked project " + str(p.ID) + ":"
		print [s.ID for s in matched]

	# For each student, get their interest in this project.
	# Add this to the sum of the overall interest.
	overall_interest = 0
	for s in matched:
		rank = s.get_ranking(p.ID)
		interest = s.get_interest_from_ranking(rank)
	 	#print "Interest is "
	 	overall_interest = overall_interest + interest
	return overall_interest

# Sort projects by highest demand to lowest demand.
def sort_projects_by_demand(students, projects):
	projects.sort(key = lambda p: get_project_interest_from_rankings(p, students), reverse = True)
	return projects


# This function takes in the already-filtered list of projects.
# Call remove infeasible projects on the original list of projects
# before calling this function.
# Initially sorts the list of projects by their overall interest levels.
# Assigns students to the projects in that order.
# Create all possible pairs of MBAs and MEngs.
# Creates all possible teams from these pairs.
# Pick the most interested team.
# Goes through the projects in terms of their sorted interest levels.

def sort_and_match_by_pairs(projects, students, verbose = False):
	if (verbose):
		print "The viable projects to match to are:"
		print "-------------------------------------"

		for p in projects:
			print names_projects[p.ID]
		print ""

	# Sort projects in order of highest demand to lowest demand.
	projects.sort(key = lambda p: get_project_interest_from_rankings(p, students), reverse = True)

	added_projects = []

	for p in projects:
		if (verbose):
			print "For " + names_projects[p.ID] + " project:"
		# Get all of the students that ranked this project.
		matched = filter(lambda s: p.ID in s.project_rankings, students)

		# Sort them into MBAs and MEngs.
		MBAs_ranked = [s for s in matched if s.degree_pursuing == 0]
		MEngs_ranked = [s for s in matched if s.degree_pursuing == 1]
		
		# Generate all possible pairs of MBAs.		
		iter_MBA_pairs = itertools.combinations(MBAs_ranked, 2)
		
		if (verbose):
			print "MBA pair IDs:"
		
		MBA_pairs = []
		MEng_pairs = []

		# Creating a list of all possible pairs
		for s in iter_MBA_pairs:
			MBA_pairs.append(s)
			if (verbose):
				(x, y) = s
				print x.ID,
				print y.ID

		# Generate all possible pairs of MEngs.
		iter_MEng_pairs = itertools.combinations(MEngs_ranked, 2)
		
		if (verbose):
			print "MEng pair IDs:"

		for s in iter_MEng_pairs:
			MEng_pairs.append(s)
			if (verbose):
				(x, y) = s
				print x.ID,
				print y.ID

		if (verbose):
			print "MEng pairs is is "
			print MEng_pairs
			print "MBA pairs is "
			print MBA_pairs

			print "Len MBA pairs",
			print len(MBA_pairs)
			print "Len MEng pairs",
			print len(MEng_pairs)

			print "There are",
			print len(MBA_pairs),
			print "MBA pairs and",
			print len(MEng_pairs),
			print "MEng pairs."

		# Generate all possible combinations of the MBAs and the MEngs.
		all_possible_teams = []
		for x in MBA_pairs:
			for y in MEng_pairs:
				all_possible_teams.append((x, y))

		if (verbose):
			string = "There are " + str(len(all_possible_teams)) + "possible teams"
			print string

		all_possible_teams_with_interest_values = []
		
		for t in all_possible_teams:
			overall_interest = 0
			((x, y), (a, b)) = t
			# Extract the members from this possible team.
			members = [x, y, a, b]

			# Get the overall interest level of this team in the project.
			for mem in members:
				rank = mem.get_ranking(p.ID)
				interest = mem.get_interest_from_ranking(rank)
				overall_interest = overall_interest + interest

			# Add an (interest, team) tuple to all
			all_possible_teams_with_interest_values.append((overall_interest, t))

		# for a in all_possible_teams_with_values:
		# 	print "(" + str(a[0]) + ","
		# 	print type(a[1])
		# 	print str(a[1].ID) + ")"
		#print ""

		#print all_possible_teams_with_values
		all_possible_teams_with_interest_values.sort(key = lambda tup: tup[0], reverse = True)
		#print all_possible_teams_with_values

		# If there are some possible teams,
		# pick the most interested one.
		if (len(all_possible_teams_with_interest_values) > 0):
			most_interested_team_combo = (all_possible_teams_with_interest_values[0])[1]
			proceed = True
	
		# If there are no possible teams, do nothing (for this project).
		else:
			#raise FieldError("There are no viable teams for project " + str(p.ID) + ".")
			proceed = False

		if (proceed):
			for tup in most_interested_team_combo:
				for stud in tup:
					p.add_student(stud)
					for s in students:
						if (s.ID == stud.ID):
							students.remove(s)

			added_projects.append(p)

	for stud in added_projects:
		stud.print_student_IDs(num = False, name = True, dct = names_projects)

	print "Remaining students are",
	print [s.name for s in students]

def get_students_from_input(file, normalize=True):
	data = pd.read_csv(file)
	data_array = np.array(data)
	shape = data_array.shape
	num_rows = shape[0]

	# Normalize our numerical variables to lie between 0 and 1.
	all_coding_abilities = data_array[:,3]
	all_work_experience = data_array[:,4]

	# TODO: instead of normalizing, should just scale it out of 1.
	# Normalization is too dependent on the values it's passed in with.
	scaled_coding_abilities = normalize_bet_zero_and_one(all_coding_abilities)
	scaled_yrs_work_experience = normalize_bet_zero_and_one(all_work_experience)
	
	students_lst = []

	# Extract rows
	for i in range(0, num_rows):
		student = data_array[i,:]
		ID 	= student[0]
		if (ID in student_ids):
			raise CompError("Student IDs must be unique.")
		student_ids.append(ID)
		
		degree_pursuing = student[1]
		cs_ug = student[2]
		coding_ability = student[3]
		num_yrs_work_exp = student[4]

		# Only take the desired number of project rankings that we want.
		rankings = student[5:(5 + classes.number_project_rankings)]
		name = student[10]

		scaled_coding_ability = scaled_coding_abilities[i]
		scaled_num_yrs_work_exp = scaled_yrs_work_experience[i]

		a = Student(name, ID, degree_pursuing, cs_ug, coding_ability, num_yrs_work_exp, rankings)

		if (normalize):
			a = Student(name, ID, degree_pursuing, cs_ug, scaled_coding_ability, scaled_num_yrs_work_exp, rankings, True)

		students_lst.append(a)

	return students_lst

def do_tests():
	students_lst = get_students_from_input("tests.csv")
	projects_filtered = remove_infeasible_projects(students_lst)
	print [p.ID for p in projects_filtered]
	#sort_and_match_by_pairs(projects_filtered, students_lst)

if (__name__ == "__main__"):
	do_tests()
