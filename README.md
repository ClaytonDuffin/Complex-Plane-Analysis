# Script for Performing Complex Plane Analysis

## Table of Contents
- [General Description](#generalDescription)
- [batcher()](#batcher)									
    - [Description](#batcherDescription)
    - [Parameters](#batcherParameters)
    - [Usage](#batcherUsage)
    - [Output](#batcherOutput)
 - [matrixMash()](#matrixMash)
    - [Description](#matrixMashDescription)
    - [Parameters](#matrixMashParameters)
    - [Usage](#matrixMashUsage)
    - [Output](#matrixMashUsage)
 - [sine()](#sine)
    - [Description](#sineDescription)
    - [Parameters](#sineParameters)
    - [Usage](#sineUsage)
    - [Output](#sineOutput)
- [complexPlaneAndSinePlot()](#complexPlaneAndSinePlot)
    - [Description](#complexPlaneAndSinePlotDescription)
    - [Parameters](#complexPlaneAndSinePlotParameters)
    - [Usage](#complexPlaneAndSinePlotUsage)
    - [Output](#complexPlaneAndSinePlotOutput)
- [goAndSavePlots()](#goAndSavePlots)
    - [Description](#goAndSavePlotsDescription)
    - [Parameters](#goAndSavePlotsParameters)
    - [Usage](#goAndSavePlotsUsage)
    - [Output](#goAndSavePlotsOutput)

+ [Suggestions for Continuation](#suggestionsForContinuation)

## General Description <a name = "generalDescription"></a>

Script used for examining the behavior of an automated trading model generated from a one-dimensional, dependent or semi-dependent time series (sine wave). This is done generally by running the strategy over the sine wave and then transforming the final units of the trading model computations (at each time-step of the sine wave) to a complex plane. The script has the capability to plot the complex plane, and then also separately, the sine wave against the last units from each time-step of trading model output. In addition to this, the script can save images of the trading model ran over the sine wave at each time-step. This functionality allows for the user to shuffle through the images either manually, or by creating a video using the individual frames.

As demonstrated in the source code, there are two primary functions that produce final output:
1.) complexPlaneAndSinePlot()
2.) goAndSavePlots()

For more specifics, or to get a better idea on all the moving parts in general, read through each function's tab, accessible via scrolling, or the Table of Contents. There are some additional functionalities not mentioned here that are mentioned there which you may find relevant or important. There are also functionalities not mentioned anywhere but the source code, such as the minMaxScaler function. Everything is documented fairly well there, so be sure to have a look if you like the script. The best way to understand how it all works, in my opinion, is to just fire it up!

I also encourage that that you play around with the parameters, and further, that you try to implement your own model by replacing the matrixMash() function. Please let me know if you come up with anything interesting, as I would love to hear about it!

## batcher() <a name = "batcher"></a>

### Description <a name = "batcherDescription"></a>
Function used for batching up a pandas DataFrame or Series object. For this application, the output data will be used for modeling.

### Parameters <a name = "batcherParameters"></a>
* sineWaveData : pd.Series
	- The input data for batching.

* subframeLength: int
	- Determines how long each subframe should be.

* gapToNextFrame: int
	- Determines the spacing between the start of one subframe and the next.

![batcherParameters1](https://user-images.githubusercontent.com/116965482/209422703-febc4210-2a6b-4dc7-b603-5f34b25f9410.png)

### Usage <a name = "batcherUsage"></a>
```
subsections = batcher(sineWave,               
		      subframeLength = 90,     
		      gapToNextFrame = 1)   
```
### Output <a name = "batcherOutput"></a>
```
produces a list of lists containing the requested batches (1 batch per row).
```

## matrixMash() <a name = "matrixMash"></a>

### Description  <a name = "matrixMashDescription"></a>
Mathematical model for generating trading signals. Quite funky. It wasn't intended, but the math has something to do with Cholesky decomposition, and Pascal's triangle, or at least this seems to be the case from my research. The idea that drove development of this model was trying to extrapolate data features from a one-dimensional time series of asset prices. 

### Parameters  <a name = "matrixMashParameters"></a>
* originalSeries : pd.Series
	- The input data for the model.


### Usage <a name = "matrixMashUsage"></a>
```
subsections = batcher(sineWave,               
		      subframeLength = 90,     
		      gapToNextFrame = 1)     

for i, j in enumerate(subsections):
	goAndSaveIndividualPlot(j, matrixMash(j), savePath)
```
### Output <a name = "matrixMashOutput"></a>
```
returns a pandas Series object
```

## sine() <a name = "sine"></a>

### Description <a name = "sineDescription"></a>
Function used to create and return a sine wave. This will be used for batching, and then the trading model will then be applied to these batches. There are parameters provided for introducing various types of wobble to the curve.

### Parameters  <a name = "sineParameters"></a>

* numberOfHertz : int, optional
	- How many hertz to use for initial generation of the sineWave.
*  sineFrequency : int, optional
    	- Can be used to steepen or flatten the curve.
* sampleSize : int, optional
	- How many x-axis ticks are wished for.
*  wobbleType: str, optional
    Takes one of four inputs:
	  *  None – Applies no wobble to the curve.
	  *  'Wobble1' – Randomly chooses to either add or subtract a random number between 1 and 10 (inclusive) divided by wobbleDegree from the sine wave at each step.
  	  * 'Wobble2' – Randomly chooses to either add or subtract a random number between 1 and 10 (inclusive) divided by wobbleDegree from the sine wave at every 10th step, and then remains at that y coordinate until the next 10th step.
  	  * 'Wobble3' – Randomly chooses to either add or subtract a random number between 1 and 10 (inclusive)  divided by wobbleDegree from the sine wave at every 10th step. The sine wave returns to normal after each 10th step.

* wobbleDegree: int, optional
	- Determines the magnitude of wobble for each of the wobbleType scenarios. As the wobbleDegree decreases, the wobble magnitude increases.

![sineParameters1](https://user-images.githubusercontent.com/116965482/209422690-155aeb21-e33f-47a0-bb61-8d011e2c345d.png)

### Usage <a name = "sineUsage"></a>
```
sineWave = sine(numberOfHertz = 780,
				sineFrequency = 2,
				sampleSize = 780,
				wobbleType = None,
				wobbleDegree = 100)
```
### Output <a name = "sineOutput"></a>
```
returns a pandas Series object
```

## complexPlaneAndSinePlot() <a name = "complexPlaneAndSinePlot"></a>

### Description <a name = "complexPlaneAndSinePlotDescription"></a>
Prior to me explaining, please check out these wikipedia diagrams:
![wikipedia Figure 1](https://upload.wikimedia.org/wikipedia/commons/a/a5/ComplexSinInATimeAxe.gif)
![wikipedia Figure 2](https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Helix_in_complex_plane.jpg/800px-Helix_in_complex_plane.jpg)

Now imagine running the trading model for the length of the sine wave (as is already being done) but then collapsing it onto the complex plane. This is what this function achieves. It also plots that newly computed complex plane, and then separately, the sine wave against the last units of the trading model at each time-step.

It is important to note and keep in mind that this method of transformation uses the last unit of the trading model at each step, and thus, other potentially valuable features generated at each step are lost in this use case. To examine these features more in-depth, refer to the goAndSavePlots() function, which stores individual images of the model, generated at each step of the sine wave for however many units were requested.

### Parameters <a name = "complexPlaneAndSinePlotParameters"></a>
* subsections : list[list]
	- The batched sections of the sine wave.
	
### Usage <a name = "complexPlaneAndSinePlotUsage"></a>
```
sineWave = sine(numberOfHertz = 780,
				sineFrequency = 2,
				sampleSize = 780,
				wobbleType = None,
				wobbleDegree = 100)

subsections = batcher(sineWave,               
		      subframeLength = 90,     
		      gapToNextFrame = 1)   
					  
complexPlaneAndSinePlot(subsections)
```

### Output <a name = "complexPlaneAndSinePlotOutput"></a>
![complexPlaneAndSinePlotOutput1](https://user-images.githubusercontent.com/116965482/209422638-0759e971-3719-48e2-abe6-ed2b5340fcbf.png)
![complexPlaneAndSinePlotOutput2](https://user-images.githubusercontent.com/116965482/209422647-dd2bf807-06c2-44c7-98eb-b03f8dc9d603.png)
![complexPlaneAndSinePlotOutput3](https://user-images.githubusercontent.com/116965482/209422657-8fe889f0-13b3-4e76-99c3-3f19d244ad15.png)

## goAndSavePlots() <a name = "goAndSavePlots"></a>

### Description <a name = "goAndSavePlotsDescription"></a>
Function used to implement the goAndSaveIndividualPlot() function for the entirety of the sine wave. The goAndSaveIndividualPlot() function is used for creating a plot showing both the sine wave, and the output from the matrixMash function computed over the sine wave. It stores the plot in a folder (defined by the user) in numerical order (1.png, 2.png etc.).

### Parameters <a name = "goAndSavePlotsParameters"></a>
* subsections : list[list]
	- The batched sections of the sine wave.
* savePath : str
	- Defines where the files are to be saved.

### Usage <a name = "goAndSavePlotsUsage"></a>
```
subsections = batcher(sineWave,               
		      subframeLength = 90,     
		      gapToNextFrame = 1)   
					  
savePath = '/Users/claytonduffin/Desktop/subDir/'
goAndSavePlots(subsections, savePath)
```
### Output  <a name = "goAndSavePlotsOutput"></a>
![goAndSavePlotsOutput](https://user-images.githubusercontent.com/116965482/209422542-bba13fe1-a327-46bc-abc5-6069361d61bc.png)


## Suggestions for Continuation <a name = "suggestionsForContinuation"></a>

1.) I suggest looking more into the complex plane, using actual financial data.  In order to do this, you might have to adjust the data to be relative to the sine wave before making computations. I would think long and hard about the proper way to do this. There is a chance that this would just take a small adjustment, and that the only issue you might come across would be trying to feed matrixMash() a pandas DataFrame instead of a pandas Series. In order to resolve this, set the sineWave parameter to say, a series of closing prices. I recommend studying how the trading model behaves relative to the different parameters it is fed and datasets it is being computed over (sine waves – with and without modifications) prior to just charting it out with real financial data, so that you can avoid bias in developing or looking for patterns if you are using this script to develop a strategy from the ground up.

2.) I suggest adding some more creative options to the sine() function's wobbleType parameter. Some conditional scenarios might be neat. I suggest going easy with it, as I feel only adjusting one feature at a time is important for better comprehension of the model in the end.
