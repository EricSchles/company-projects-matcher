#import teams
import numpy as np
import pandas as pd
from sklearn import preprocessing
from scipy import linalg
from scipy import spatial
from statsmodels.stats import correlation_tools
import clustering
import math

default_file = "/Users/ameyaacharya/Documents/Projects/Company Projects/Code/company-projects-matcher/data/survey_responses.csv"

class DistanceError(Exception):
	def __init__(self, value):
		self.val = value
	def __str__(self):
		return repr(self.val)

def weight_interest(x):
	# TODO: change this to be in the range of valid interest vals.
	# If this dict doesn't exist, make it.
	# Maybe don't need to do this if it's passed in the right time?
	if (not(x in range(1, 11))):
		raise DistanceError("Interest value is invalid.")
	a = 10 * x
	return a * math.sqrt(a)

def is_positive_semidefinite(cov_matrix, verbose = False):
#Calculates all eigenvalues of the matrix
# If there are negative eigenvalues, returns false.
	(eigenvalues, eigenvectors) = linalg.eig(cov_matrix)
	res = []
	#print eigenvalues.shape
	for e in eigenvalues:
		#print e
 		if (e < 0):
	 		res.append(e)
	if (verbose):
		print "Negative eigenvalues of covariance matrix are:"
		print res
	return len(res) == 0

# Reads the data from the file (if we need to fix how the data is read, change clustering init.)
# Preprocesses data with one hot encoding (changes categorical variables into numerical.)
# Fixes matrix if it's not positive semidefinite (adds a small version of the identity.)
# Returns (data, covariance matrix.)
def create_covariance_matrix(file = default_file, verbose = False):
	data_array = clustering.__init__(file)
	one_hot_data_preprocessed = clustering.do_preprocessing(data_array)
	
	if (verbose):
		print "One hot data preprocessed is: "
		print one_hot_data_preprocessed
		print one_hot_data_preprocessed.shape

	# rowvar = 0 because each column represents a variable, while the rows are observations
	covariance_matrix = np.cov(one_hot_data_preprocessed, rowvar = 0)
	if (verbose):
		print "Covariance matrix is:"
		print covariance_matrix
	shape = covariance_matrix.shape
	num_rows = shape[0]
	num_cols = shape[1]
	
	# Should never happen
	if (not(num_rows == num_cols)):
		raise DistanceError("Covariance matrix is not a square matrix.")

	else:
		if (is_positive_semidefinite(covariance_matrix)):
			if (verbose):
				print "Pos semi def on the first try!"
			pass		
		# Our covariance matrix is not positive semidefinite -- an arithmetic error.
		# Will add (a small number * the identity matrix) to covariance matrix to fix this error.
		else:
			if (verbose):
				print "Not pos semi def on the first try!"
			n = num_rows
			i = np.array(np.identity(n))
			factor = 10. ** -10
			# Create a matrix that is a small number times the identity.
			small_identity = np.multiply(i, factor)

			# Add that matrix to our covariance matrix (to make sure that our matrix is positive semidefinite.)
			result = np.add(small_identity, covariance_matrix)
			if (not(is_positive_semidefinite(result))):
				raise DistanceError("Fixed covariance matrix is not positive semidefinite.")
			else:
				covariance_matrix = result

	return (data_array, one_hot_data_preprocessed, covariance_matrix)

# Calcuate matrix square root using scipy linalg
def sqrt_covariance_matrix(covariance_matrix):	
 	matrix_square_root = linalg.sqrtm(covariance_matrix)
	return matrix_square_root

def inverse_matrix(sqrt_covariance_matrix, use_pseudo_inv = True, verbose = False):
	
	# Calculate real matrix inverse.
	if (not(use_pseudo_inv)):
	 	cov_inverse = linalg.inv(sqrt_covariance_matrix)
	 	if (verbose):
	 		print "(Real) inverse of the sqrt. covariance matrix is: "

	# Calculate the matrix pseudoinverse.
	else:
	 	cov_inverse = np.linalg.pinv(sqrt_covariance_matrix)
	 	if (verbose):
			print "(Pseudo) inverse of the sqrt. covariance matrix is: "

	#print cov_inverse
	return cov_inverse

# Implements:
# f(x, y) = 
# 	1 IF x = y
# 	0.75 IF abs(x - y) = 1
# 	1/(abs(x-y)) otherwise
# NOTE: x, y in [0, 4] for coding ability, and x, y in [0, 6] for work experience
def calc_numerical_difference(x, y, verbose = False):
	if (verbose):
		print "In calc numer diff:"
		print "X is " + str(x)
		print "Y is " + str(y)
	if (x == y):
		return 1.0
	elif (abs(x - y) == 1):
		return 0.75
	else:
		return (1.0 / ((abs(x-y))*1.0))

def subtract_vectors(s_one_properties, s_two_properties, verbose = False):

	# Extract the values of interest
	# ca_one = s_one_properties[10]
	# ca_two = s_two_properties[10]
	# work_one = s_one_properties[11]
	# work_two = s_two_properties[11]

	# s_one_properties[10] = 0
	# s_two_properties[10] = 0
	# s_one_properties[11] = 0
	# s_two_properties[11] = 0

	# Calculate our function for these values

	#coding_diff = calc_numerical_difference(ca_one, ca_two)
	#work_diff = calc_numerical_difference(work_one, work_two)

	a = np.subtract(s_one_properties, s_two_properties)
	a = np.absolute(a)

	print "Absolute value of subtracted vectors is:"
	print a
	
	#res = res + coding_diff + work_diff

	#return res

	
	
def do_mahal_distance(s_one_properties, s_two_properties, inv_sq_cov_mat, verbose = False, fixed_with_zeros = True):
	
	# TODO: not sure if we even want to use this.
	# obs_zero = one_hot_data_preprocessed[0]
	# obs_one = one_hot_data_preprocessed[1]
	# print "Mahal distance is " + str(spatial.distance.mahalanobis(obs_zero, obs_one, cov_inverse))


	if (fixed_with_zeros):
	# Reset these values in copies the original vectors to 0
	# so they don't affect the dot products.

		# Copy the original vectors over, so that we don't modify them.
		# (When we loop through all of the data, we'll have to reuse it.)
		copy_s_one = s_one_properties.copy()
		copy_s_two = s_two_properties.copy()

		# Extract the values of interest
		ca_one = copy_s_one[10]
		ca_two = copy_s_two[10]
		work_one = copy_s_one[11]
		work_two = copy_s_two[11]
		
		copy_s_one[10] = 0
		copy_s_two[10] = 0
		copy_s_one[11] = 0
		copy_s_two[11] = 0

		# Calculate numerical differences using above function
		coding_diff = calc_numerical_difference(ca_one, ca_two)
		work_diff = calc_numerical_difference(work_one, work_two)

		# Dot the copied vectors
		a = np.dot(copy_s_one, inv_sq_cov_mat)
		res = np.dot(a, copy_s_two)

		if (verbose):
			print "Dotted value: " + str(res)
			print "Calculated values:",
			print coding_diff,
			print work_diff

		# Add the calculated differences.
		new_res = res + coding_diff + work_diff
		if (verbose):
			print "New res is " + str(new_res)
		return new_res

	else:

		a = np.dot(s_one_properties, inv_sq_cov_mat)
		res = np.dot(a, s_two_properties)

		return res

# Pass in team of Students.
# TODO: make a Team ID, and return (Team_ID, result.)
def average_mahal_distance_team(team):
	result = []
	for mem_one in team:
		for mem_two in team:
			if (not(mem_one.ID == mem_two.ID)):
				result.append(do_mahal_distance(mem_one, mem_two))
	return np.mean(result)

def do_and_sort_all_mahal_dists(set_of_teams):
	result = []
	for team in set_of_teams:
		result.append(average_mahal_distance_team)
	return result.sort()

def use_python_distance_data(student_one, student_two, inv_sq_cov_mat):
	return spatial.distance.mahalanobis(student_one, student_two, inv_sq_cov_mat)
	
# The input "python" decides if we use the built-in mahalanobis distance or not
def do_all_distances_data(data, inv_sq_cov_mat, unprocessed_data, start = 0, verbose = False, python = False):
	i = start
	j = start
	res = []
	if (verbose):
		print "data is " + str(data)
	for student_one in data:
		for student_two in data:
			if (verbose):
				#print "(i, j) = " + str((i, j))
				print "Student one is: " + str(student_one)
				print "Student two is: " + str(student_two)
			#d = np.dot(student_one, student_two)
			if (not(python)):
				if (verbose):
					print "Using my distance"
			 	d = do_mahal_distance(student_one, student_two, inv_sq_cov_mat, fixed_with_zeros = True)
			 	if (verbose):
			 		print "d is " + str(d)
			else:
				d = use_python_distance_data(student_one, student_two, inv_sq_cov_mat)
			# names = (data[i], data[j])
			# print str(names) + str(d)
			tup = ((i, j), d)
			keys = [t[0] for t in res]
			if ((j, i) in keys):
			 	pass
			else:
			 	res.append(tup)
			j += 1
		i += 1
		j = start
	res.sort(key = lambda tup: tup[1])

	#minimum_tuple = res[0]
	#minimum = minimum_tuple[1]
	if (True):
		 for i in res:
		 	tup = i[0]
		 	first_student = tup[0]
			second_student = tup[1]

			lst_first_student = unprocessed_data[first_student]
			lst_second_student = unprocessed_data[second_student]
 
			#print "(",
			# print "UG major: " + str((lst_first_student[0], lst_second_student[0]))
			# print "Coding ability: " + str((lst_first_student[1], lst_second_student[1]))
			# print "Degree pursuing: " + str((lst_first_student[2], lst_second_student[2]))
			# print "Work exp. (yrs) " + str((lst_first_student[3], lst_second_student[3]))
			# print ")",

			print lst_first_student
			print lst_second_student

			for x in range(0, 4):
				if (not(lst_first_student[x] == lst_second_student[x])):
					print "Diff at " + str(x)
					pass

			#print i[1] - minimum
			print i[1]

	#return res

if (__name__ == "__main__"):
	# Will print out the entire matrix if necessary
	np.set_printoptions(threshold=np.nan)

	tup = create_covariance_matrix(file = "/Users/ameyaacharya/Documents/Projects/Company Projects/Code/company-projects-matcher/data/survey_responses_altered.csv")
	unprocessed_data = tup[0]
	processed_data = tup[1]
	covariance_matrix = tup[2]

	sq_cov = sqrt_covariance_matrix(covariance_matrix)
	inv_sq_cov = inverse_matrix(sq_cov)
	#print inv_sq_cov

	# print "d unprocessed " + str(unprocessed_data[1])
	# print "d processed " + str(processed_data[1])

	# print "e unprocessed " + str(unprocessed_data[34])
	# print "e processed " + str(processed_data[34])


	#print "unprocessed_data " + str(unprocessed_data)
	#print "processed_data " + str(processed_data)
	#d_clustered = clustering.do_preprocessing(unprocessed_data[1])
	
	# d_u = unprocessed_data[11]
	# d_p = processed_data[11]
	# e = processed_data[18]
	# f = processed_data[15]
	# small_processed_data = (d_p, d_p, d_p)
	# small_unprocessed_data = (d_u, d_u, d_u)
	# print small_processed_data
	# print small_unprocessed_data
	#print "Before inputing to mahal distances " + str(small_data)
	# #f = processed_data[32]
	# print "d " + str(unprocessed_data[1])
	# print "e " + str(unprocessed_data[34])
	# #print "f" + str(f)
	#print "(d, d)",
	#print do_mahal_distance(d, d, inv_sq_cov)
	#print "(d, e)",
	#print do_mahal_distance(d, e, inv_sq_cov)

	# print "Small data is: " + str(small_data)

	# SMALL DATA: to test something
	#do_all_distances_data(small_processed_data, inv_sq_cov, small_unprocessed_data, verbose = True)

	# BIG DATA: for reals
	#do_all_distances_data(processed_data, inv_sq_cov, unprocessed_data, verbose = True)

	# Testing weighted interest
	#for i in range (1, 11):
		#print str(i) + ": " + str(weight_interest(i))
	

	#print "Square root of covariance matrix is: "
	#print sq_cov

	#print "Eigenvalues are: "
	#print linalg.eig(cov)

	# SANITY CHECKS for matrix square root
	#print "Eigenvalues of square root are:"
	#print linalg.eig(sq_cov)

	# STUPID NP.MULTIPLY WAS GIVING ME THE WRONG ANSWERS
	#c = np.dot(sq_cov, sq_cov)
	#print "Covariance matrix is: "
	#print covariance_matrix
	#print "Sqrt multiplied by itself:"
	#print c
	#print "Covariance matrix minus sqrt*sqrt:"
	#print covariance_matrix - c
	#print (c == covariance_matrix)
	#inverse_matrix(sq_cov)




