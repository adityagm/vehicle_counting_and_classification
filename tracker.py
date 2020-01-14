# import the necessary packages
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np

class CentroidTracker():
	def __init__(self, maxDisappeared=50):
		# initialize the next unique object ID along with two ordered
		# dictionaries used to keep track of mapping a given object
		# ID to its centroid and number of consecutive frames it has
		# been marked as "disappeared", respectively
		self.nextObjectID = 0
		self.objects = OrderedDict()
		self.disappeared = OrderedDict()

		# store the number of maximum consecutive frames a given
		# object is allowed to be marked as "disappeared" until we
		# need to deregister the object from tracking
		self.maxDisappeared = maxDisappeared

	def register(self, centroid):
		# when registering an object we use the next available object
		# ID to store the centroid
		self.nextObjectID += 1
		self.objects[self.nextObjectID] = centroid
		self.disappeared[self.nextObjectID] = 0
		return self.nextObjectID

	def deregister(self, ID):
		self.disappeared[ID] = 1
		if ID in self.objects.keys():
			del self.objects[ID]

	def update(self, centroid):
		# check to see if the list of input bounding box rectangles
		# is empty
		acentroid = np.array([centroid])
		#print(acentroid)
		# if we are currently not tracking any objects take the input
		# centroids and register each of them
		if len(self.objects) == 0:
			objectID = self.register(centroid)

			#print(self.objects)

		# otherwise, are are currently tracking objects so we need to
		# try to match the input centroids to existing object
		# centroids
		else:
		# 	# grab the set of object IDs and corresponding centroids
			objectIDs = list(self.objects.keys())
			objectCentroids = list(self.objects.values())
			#
			# 	# compute the distance between each pair of object
			# 	# centroids and input centroids, respectively -- our
			# 	# goal will be to match an input centroid to an existing
			# 	# object centroid
			# 	# objectCentroids = np.array(objectCentroids)
			#print(objectCentroids)
			D = dist.cdist(acentroid, objectCentroids)
			#
			#
			# 	# in order to perform this matching we must (1) find the
			# 	# smallest value in each row and then (2) sort the row
			# 	# indexes based on their minimum values so that the row
			# 	# with the smallest value as at the *front* of the index
			# 	# list
			rows = D.min(axis=1).argsort()
			#print(rows)
			# 	# next, we perform a similar process on the columns by
			# 	# finding the smallest value in each column and then
			# 	# sorting using the previously computed row index list
			cols = D.argmin(axis=1)[rows]

			distance = D[rows[0]][cols[0]]
			if distance < 2:
				objectID = objectIDs[cols[0]]
				self.objects[objectID] = centroid
				print(self.objects)
			else:
				objectID = self.register(centroid)

		# # return the set of trackable objects
		return objectID