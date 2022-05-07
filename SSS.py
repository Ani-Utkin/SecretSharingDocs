# Template from https://www.geeksforgeeks.org/implementing-shamirs-secret-sharing-scheme-in-python/
# An implementation of Shamir's Secret Sharing
import random
PRIME = 127

def reconstruct_secret(shares):
	
	
	x = 0
	secret = 0

	for i in range(len(shares)):
		p = 1
		for j in range(len(shares)):
			if i != j and (shares[i][0] - shares[j][0]):
				p *= (x - shares[j][0]) * pow((shares[i][0] - shares[j][0]), -1, PRIME)

		secret += (p * shares[i][1]) % PRIME
	
	secret = secret % PRIME

	return secret


def polynom(x, coefficients):
	point = 0
	# Loop through reversed list, so that indices from enumerate match the
	# actual coefficient indices
	for coefficient_index, coefficient_value in enumerate(coefficients[::-1]):
		point += (x ** coefficient_index) * coefficient_value

	return point % PRIME


def coeff(threshold, secret):

	coeff = [random.randrange(1, PRIME - 1) for _ in range(threshold - 1)]
	coeff.append(secret)
	return coeff


def generate_shares(num_shares, threshold, secret):

	coefficients = coeff(threshold, secret)
	shares = []

	for _ in range(1, num_shares+1):
		x = random.randrange(1, PRIME - 1)
		shares.append((x, polynom(x, coefficients)))

	return shares
