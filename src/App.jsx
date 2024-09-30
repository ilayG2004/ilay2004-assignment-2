import { useState, useEffect } from 'react';
import './App.css';
import Plot from 'react-plotly.js';

function App() {
  const [method, setMethod] = useState('random');
  const [isLoading, setIsLoading] = useState(true);
  const [kmeansLoading, setKmeansLoading] = useState(false);
  const [kmeansSteps, setKmeansSteps] = useState([]);
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState({ points_x: [], points_y: [] });
  const [numClusters, setNumClusters] = useState(2);
  const [manualCenters, setManualCenters] = useState([]);

  // Fetch random data points
  const fetchGraph = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/random');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setData(data);
      setCurrentStep(0); // Reset step when new data is generated
      setKmeansSteps([]); // Clear previous KMeans steps
      await fetchKmeansSteps(); // Automatically fetch KMeans steps

    } catch (error) {
      console.error('Error fetching the scatter plot:', error);
    } finally {
      setIsLoading(false);
    }

  };

  const fetchKmeansSteps = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/randomcentroid', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ method, manual_centers: manualCenters, k: numClusters }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setKmeansSteps(data.kmeans_steps);
      console.log(kmeansSteps.length);
      setCurrentStep(0);
    } catch (error) {
      console.error('Error fetching KMeans steps:', error);
    } finally {
      setKmeansLoading(false);
    }
  };

  const nextStep = () => {
    if (currentStep < kmeansSteps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };
  const finalStep = () => {
    if (kmeansSteps.length > 0) {
      setCurrentStep(kmeansSteps.length - 1);
      console.log(kmeansSteps.length);
      console.log(currentStep);
    }
  };
  const handlePlotClick = (event) => {
    if (event.points.length > 0 && method == 'manual') {
      const x = event.points[0].x; //Get x coordinate from the clicked point
      const y = event.points[0].y; //Get y coordinate from the clicked point

      //Update manual centers state with new click coordinates
      setManualCenters((prevCenters) => [...prevCenters, [x, y]]);
    }
    console.log(manualCenters)
  };


  const renderPlot = () => {
    //Error checking. No steps to render
    if (kmeansSteps === 0) {
      return null;
    }
    //Error checking. No steps to render
    if (kmeansSteps.length === 0) {
      return null;
    }

    const step = kmeansSteps[currentStep];
    if (!step) {
      return null; // Guard against undefined step
    }

    //Extract centers and assignments from the current step
    const centers = step.centers;
    const assignments = step.assignments;

    //Get all data points
    const plotPoints = {
      x: data.points_x,
      y: data.points_y,
      mode: 'markers',
      type: 'scatter',
      marker: {
        color: assignments,
        colorscale: 'Viridis',
        showscale: true,
        size: 10,
      },
      name: 'Data Points',
    };

    //Get all centers
    const plotCenters = {
      x: centers.map(center => center[0]),
      y: centers.map(center => center[1]),
      mode: 'markers',
      type: 'scatter',
      marker: {
        color: 'red',
        size: 12,
        symbol: 'cross',
      },
      name: 'Centers',
    };
    return (
      <Plot
        data={[plotPoints, plotCenters]}
        layout={{
          title: 'KMeans Clustering Steps',
          xaxis: { title: 'X' },
          yaxis: { title: 'Y' },
          showlegend: true,
          height: 400,
          width: 600,
          hovermode: 'closest',
        }}
        onClick={handlePlotClick}
      />
    );
  };

  useEffect(() => {
    //Grab random data when starting webpage
    fetchGraph();
  }, []);

  const handleNumClustersChange = (e) => {
    setNumClusters(e.target.value);
  };
  const resetEverything = (e) => {
    setManualCenters([]);
    setIsLoading(true);
  };
  useEffect(() => {
    if (isLoading) {
      fetchGraph(); //When button is hit, rerun and grab new random plot
    }
  }, [isLoading]);
  return (
    <>
      <h2>Number of Clusters (k)</h2>
      <input type='text' id='num_clusters' name='Number of Clusters (k)' value={numClusters}
        onChange={handleNumClustersChange}></input>
      <h2>Initialization Method</h2>
      <select
        name='initialization'
        value={method}
        onChange={(e) => setMethod(e.target.value)}
      >
        <option value='random'>Random</option>
        <option value='farthest_first'>Farthest First</option>
        <option value='kmeans++'>KMeans++</option>
        <option value='manual'>Manual</option>
      </select>
      <div className='card'>
        <button onClick={fetchGraph}>Generate New Data Set</button><br />
        <button onClick={nextStep}>Step Through KMeans</button><br />
        <button onClick={finalStep}>Run to Convergence</button><br />
        <button onClick={resetEverything}>Reset Algorithm</button><br />
      </div>
      <h1>Random ScatterPlot</h1>
      <div className='image-container'>
        {isLoading ? (
          <p>Loading...</p>
        ) : (
          renderPlot()
        )}
      </div>
    </>
  );
}

export default App;
