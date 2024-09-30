from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import io
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from PIL import Image as im
import sklearn.datasets as datasets
import base64

app = Flask(__name__)
CORS(app)

#Save the random plot data for later so we can run different versions of kmeans on it
plot_data = {
  'points_x': np.array([]),
  'points_y': np.array([])
}

numpy_plot = None
k = 2
#Return an image of a randomly generated plot without any clusters on it yet
@app.route("/random")
def random_plot():
  global plot_data
  global numpy_plot

  n_bullets = 100
  plot_data['points_x'] = np.asanyarray([random.randint(-10,10) for _ in range (n_bullets)])
  plot_data['points_y'] = np.asanyarray([random.randint(-10,10) for _ in range (n_bullets)])
  
  return jsonify(
        points_x=plot_data['points_x'].tolist(),
        points_y=plot_data['points_y'].tolist(),
        assignments=[],  # Empty assignments for the random data
        centers=[]       # No centers for the random data
    )

class KMeans:
  def __init__(self, data, k, method='random', manual_centers=None):
      self.data = data
      self.k = k
      self.assignment = [-1 for _ in range(len(data))]
      self.snaps = []
      self.method = method
      self.manual_centers = manual_centers
      self.steps = []

  def snap(self, centers):
      step = {
            "centers": centers.tolist(),  # Convert numpy arrays to lists for JSON
            "assignments": self.assignment[:],  # Copy the current assignments
        }
      self.steps.append(step)

  def is_unassigned(self, i):
      return self.assignment[i] == -1

  def initialize(self):
      if len(self.data) < self.k:
            raise ValueError("Number of clusters (k) cannot be greater than the number of data points.")
      if self.method == 'random':
        return self.data[np.random.choice(len(self.data) - 1, size=self.k, replace=False)]
      elif self.method == 'farthest_first':
        initial_centroid_idx = np.random.randint(self.data.shape[0]) # Get random data point index
        initial_centroid = self.data[initial_centroid_idx]           # Retrieve the data point associated with that index
        centroids = [initial_centroid]                          # Put the data point into a list with centroid locations
        for _ in range (1, self.k):                              #Take the euclidian distance from the data point to all centroids, find the furthest minimum distance
            distances = []
            for point in self.data:
                dists = self.euclidian_dist(point, centroids)
                distances.append(np.min(dists))
            max_idx = np.argmax(distances)
            centroids.append(self.data[max_idx])
        return centroids
      elif self.method == 'kmeans++':
        #Start with random center
        #Let D(x) be the distance between x and the closest of the centers picked so far. Choose the next center with probability proportional to D(x)^2
        #This allows us to get nicely spread out centers. Since the further points will have a higher probability of being chosen
        initial_centroid_idx = np.random.randint(self.data.shape[0])
        initial_center = self.data[initial_centroid_idx]
        centers = [initial_center]            
        for _ in range (1, self.k):
              distances = np.min([np.linalg.norm(self.data - center, axis=1)**2 for center in centers], axis=0)


              probabilities = distances / np.sum(distances)
              next_center = self.data[np.random.choice(self.data.shape[0], p=probabilities)]
              centers.append(next_center)
        return np.array(centers)
      elif self.method == 'manual':
          #Convert the size 2 list of x & y into a numpy array. (For the sake of time it was easier storing the coordinates as a list instead of a tuple)
          centers = []
          for center in self.manual_centers:
              centers.append(np.array(center)) 
          return centers
          
  
  def make_clusters(self, centers):
      for i in range(len(self.assignment)):
          for j in range(self.k):
              if self.is_unassigned(i):
                  self.assignment[i] = j
                  dist = self.dist(centers[j], self.data[i])
              else:
                  new_dist = self.dist(centers[j], self.data[i])
                  if new_dist < dist:
                      self.assignment[i] = j
                      dist = new_dist

  def compute_centers(self):
      centers = []
      for i in range(self.k):
          cluster = []
          for j in range(len(self.assignment)):
              if self.assignment[j] == i:
                  cluster.append(self.data[j])
          centers.append(np.mean(np.array(cluster), axis=0))
      return np.array(centers)

  def unassign(self):
      self.assignment = [-1 for _ in range(len(self.data))]

  def are_diff(self, centers, new_centers):
      for i in range(self.k):
          if self.dist(centers[i], new_centers[i]) != 0:
              return True
      return False

  def dist(self, x, y):
      return sum((x - y)**2) ** (1/2)
  
  def euclidian_dist(self, point, centroids):
      dist = np.sqrt(np.sum((point - centroids) ** 2, axis=1))
      return dist

  def lloyds(self):
      centers = self.initialize()
      self.make_clusters(centers)
      new_centers = self.compute_centers()
      self.snap(new_centers)
      while self.are_diff(centers, new_centers):
          self.unassign()
          centers = new_centers
          self.make_clusters(centers)
          new_centers = self.compute_centers()
          self.snap(new_centers)
      return self.steps


def run_kmeans(data,k, method, manual_centers):
  kmeans = KMeans(data, k, method, manual_centers)
  kmeans.lloyds()
  return kmeans.steps




@app.route("/randomcentroid", methods=['POST', 'GET']) 
def random_centroid():
    global plot_data
    
    if request.method == 'POST':
        client = request.get_json(silent=True) or {}
        clientMethod = client.get('method', 'random')
        clientManual_Centers = client.get('manual_centers', None)
        clientClusters = int(client.get('k', '2'))

        #Convert manual centers from list of lists to numpy array if provided
        if clientManual_Centers is not None:
            clientManual_Centers = [np.array(center) for center in clientManual_Centers]

    else:
        clientMethod = 'random'

    #If plot data wasn't made yet, create it
    if plot_data['points_x'].size == 0 or plot_data['points_y'].size == 0:
        random_plot()

    #Reformat plot_data table for kmeans
    data = np.column_stack((plot_data['points_x'], plot_data['points_y']))

    print(f"Data shape: {data.shape}")
    print(data)

    #Verify data is valid
    if data.shape[0] < 1:
        return jsonify(error="No data available for clustering"), 400
    
    try:
        kmeans_steps = run_kmeans(data, clientClusters, clientMethod, clientManual_Centers)
        return jsonify(kmeans_steps=kmeans_steps)
    except Exception as e:
        print("Error during KMeans processing:", e)
        return jsonify(error="An error occurred during KMeans processing"), 500

if __name__ == "__main__":
  app.run(debug=True)