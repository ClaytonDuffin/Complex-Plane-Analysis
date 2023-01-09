import multiprocess
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt; plt.rcdefaults()
from matplotlib.ticker import MultipleLocator
from tqdm import tqdm
from itertools import chain
from typing import Union, Optional
import operator
import random
import warnings
warnings.simplefilter(action = 'ignore', category = pd.errors.PerformanceWarning)
plt.rc('figure', max_open_warning = 0)


def batcher(sineWaveData: Union[pd.Series, pd.DataFrame],
            subframeLength: int, 
            gapToNextFrame: int) -> list:
    
    '''
    Function used for batching up a pandas DataFrame or Series object. The output data will be used for modeling.
    
    Parameters
    ----------   
    sineWaveData : pd.Series
        The input data for batching.
    subframeLength: int
        Determines how long each subframe should be.
    gapToNextFrame: int
        Determines the spacing between the start of one subframe and the next. 
    '''

    if isinstance(sineWaveData, pd.Series):
        originalData = list(zip(sineWaveData))
    else:
        originalData = list(zip(*[sineWaveData[col] for col in sineWaveData.columns[1:]]))

    fullSeries = []
    for t, j in enumerate(originalData):
        subSeries = [] 
        for i in range(0, subframeLength, gapToNextFrame):
            try:
                subSeries.append(originalData[t-i])
            except IndexError:
                continue
            
        fullSeries.append(list(chain(*[list(row) for row in subSeries[::-1]])))
        
    return fullSeries


def matrixMash(originalSeries: pd.Series) -> pd.Series:
    
    '''
    Mathematical model for generating trading signals. Quite funky.
    It wasn't intended, but the math has something to do with Cholesky decomposition,
    and Pascal's triangle, or at least this seems to be the case from my research.
    The idea that drove development of this model was trying to extrapolate data features
    from a one-dimensional time series of asset prices. 
       
    Parameters
    ----------   
    originalSeries : pd.Series
        The input data for the model.
    '''
    
    constructorSeries = []
    constructorSeries.append(originalSeries)
    
    for k in constructorSeries: 
        while len(constructorSeries[-1]) > 1:
            constructorSeries.append(([j - constructorSeries[-1][i - 1] for i, j in enumerate(constructorSeries[-1])][1:]))
    
    differenceFrames = pd.DataFrame(constructorSeries[1:(len(constructorSeries))]).T
    
    placeholderList = []
    for i in range(len(differenceFrames)):
        placeholderList.append(differenceFrames[i].shift(len(differenceFrames) - (differenceFrames[i].count())))
    
    arrangedDifferences = pd.concat(placeholderList, axis = 1)
    diagonalMatrix = (arrangedDifferences + arrangedDifferences.T)/2
    symmetricMatrixX2 = arrangedDifferences.fillna(0) + arrangedDifferences.T.fillna(0)
    finishedMatrix = symmetricMatrixX2 - (diagonalMatrix.fillna(0))
        
    return (pd.DataFrame(finishedMatrix)).rank().mean(axis = 1)


def sine(numberOfHertz: Optional[int] = 780, 
         sineFrequency: Optional[int] = 2,
         sampleSize: Optional[int] = 780,
         wobbleType: Optional[str] = None,
         wobbleDegree: Optional[int] = 100) -> pd.Series:
            
    '''
    Function used to create and return a sine wave. This will be used for batching, and the 
    trading model will then be applied to these batches of the sine wave. There are parameters
    provided for introducing various types of wobble to the curve.
    
    Parameters
    ----------   
    numberOfHertz : int, optional
        How many hertz to use for initial generation of the sineWave.
    sineFrequency : int, optional
        Can be used to steepen or flatten the curve.
    sampleSize : int, optional
        How many x-axis ticks are wished for.
    wobbleType: str, optional
        Takes one of four inputs:
            None -------- Applies no wobble to the curve.
            'Wobble1' --- Randomly chooses to either add or subtract a random number between 1 and 10 (inclusive) 
                          divided by wobbleDegree from the sine wave at each step.
            'Wobble2' --- Randomly chooses to either add or subtract a random number between 1 and 10 (inclusive) 
                          divided by wobbleDegree from the sine wave at every 10th step, and then remains at that y coordinate until the next 10th step.
            'Wobble3' --- Randomly chooses to either add or subtract a random number between 1 and 10 (inclusive) 
                          divided by wobbleDegree from the sine wave at every 10th step. The sine wave returns to normal after each 10th step.
    wobbleDegree: int, optional
        Determines the magnitude of wobble for each of the wobbleType scenarios. As the wobbleDegree decreases, the wobble magnitude increases.
    '''

    x = np.arange(sampleSize)
    y = np.sin(2 * np.pi * sineFrequency * x / numberOfHertz)
    y2 = []
    
    if (wobbleType == None):
        sineWave = pd.DataFrame([x,y]).T
        return sineWave[1]
    
    if (wobbleType == 'Wobble1'):
        for i, j in enumerate(y):
            y2.append(random.choice([operator.add, operator.sub])(j, (random.randint(1, 10)) / wobbleDegree))
    
    if (wobbleType == 'Wobble2') | (wobbleType == 'Wobble3'):
        for i, j in enumerate(y):
            if ((i % 10) == 0):
                newY = random.choice([operator.add, operator.sub])(j, (random.randint(1, 10)) / wobbleDegree)
                y2.append(newY)
            else:
                if (wobbleType == 'Wobble2'):
                    y2.append(newY)
                elif (wobbleType == 'Wobble3'):
                    y2.append(j)
                    
    sineWave = pd.DataFrame([x,y2]).T
    return sineWave[1]


def minMaxScaler(frame: pd.DataFrame,
                 lower: Optional[float] = 0.5,
                 upper: Optional[float] = 1.5) -> pd.DataFrame:
    '''
    Scales a dataframe to a range specified by the parameters.
    
    Parameters
    ----------
    frame : pd.DataFrame
        The DataFrame to be scaled.
    lower : float
        The global minimum of the data is to be rescaled to this number.
    upper : float
        The global maxmimum of the data is to be rescaled to this number.
    '''
    
    freshlyScaled = []
    for i in frame:
        newLower, newUpper, oldLower, oldUpper =  lower, upper, frame[i].min(), frame[i].max()
        freshlyScaled.append((frame[i] - oldLower) / (oldUpper - oldLower) * (newUpper - newLower) + newLower)

    return (pd.DataFrame(freshlyScaled).T)


def complexPlaneAndSinePlot(subsections: list[list]) -> None:
    
    '''
    Check out these wikipedia diagrams: 
                                    https://upload.wikimedia.org/wikipedia/commons/a/a5/ComplexSinInATimeAxe.gif
                                    https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Helix_in_complex_plane.jpg/800px-Helix_in_complex_plane.jpg
                                    
    Now imagine running the trading model for the length of the sine wave (as is already being done) but then collapsing it onto the complex plane. 
    This is what this function achieves. It also plots that newly computed complex plane, and the sine wave against the last units of the trading model 
    at each time step. It is important to note and keep in mind that this method of transformation uses the last unit of the trading model at each step, 
    and thus, other potentially valuable features generated at each step are lost in this use case.
 
     Parameters
     ----------   
     subsections : list[list]
         The batched sections of the sine wave.
     '''
         
    with multiprocess.Pool(multiprocess.cpu_count()) as pool:
        finalUnitsOfModelSteps = [list(i.tail(1)) for i in tqdm(pool.imap(matrixMash, [i for i in subsections[0: int(len(subsections) / 2)]]), total = int(len(subsections) / 2))] # only uses half of the sineWave since default frequency is 2

    potentialInsights = pd.DataFrame(list(chain(*(finalUnitsOfModelSteps))))
    scaledPotentialInsights = minMaxScaler(potentialInsights)
    fullT = np.linspace(np.pi, -np.pi, len(potentialInsights))
    newT = pd.concat([pd.DataFrame(fullT[(int(len(potentialInsights) / 4)) : (int(len(potentialInsights)))].tolist()),
                      pd.DataFrame(fullT[0 : int(len(potentialInsights) / 4)].tolist()),]).reset_index(drop=True).to_numpy()  #note here, I am reorganizing the fullT values so that they will corresponded to the order of the sine wave
    
    radius = 1
    x, y = [], []
    for i, j in enumerate(newT):
        x.append((scaledPotentialInsights.loc[i]) * (radius * np.sin(j)))
        y.append((scaledPotentialInsights.loc[i]) * (radius * np.cos(j)))

    fig = plt.figure(figsize = [10, 10])
    plt.plot(x,y, color = 'black', linewidth = 2)
    plt.plot((1.5 * (((radius * np.sin(fullT))))), (1.5 * (((radius * np.cos(fullT))))), color = 'firebrick', linewidth = 1)
    plt.plot((0.5 * (((radius * np.sin(fullT))))), (0.5 * (((radius * np.cos(fullT))))), color = 'firebrick', linewidth = 1)
    plt.title('Trading Model over Sine Wave as Complex Plane', size = 20)
    plt.text(1, 1.3,'\nQuadrant I: \n first subset \n of sine wave', fontsize = 12)
    plt.text(-1.5, 1.3,'\nQuadrant II: \n second subset \n of sine wave', fontsize = 12)
    plt.text(-1.5, -1.5,'\nQuadrant III: \n third subset \n of sine wave', fontsize = 12)
    plt.text(1, -1.5,'\nQuadrant IV: \n fourth subset \n of sine wave', fontsize = 12)
    plt.axvline(0, linewidth = 1, color = 'black')
    plt.axhline(0, linewidth = 1, color = 'black')
    plt.axis('equal')
    plt.pause(0.01)
    
    fig, axes = plt.subplots(2,1, figsize=[14.275,14.275], sharex=True)
    axes[0].plot(pd.DataFrame(sineWave[0:390]), color = 'black',linewidth = 1) # be sure to note that this variable is not defined locally.
    axes[1].plot(potentialInsights, color = 'black',linewidth = 1)
    axes[0].set_title('Final Units of Trading Model at Each Step of Sine Wave', size = 20)
    axes[0].text(22, 0.1,'\nQuadrant I', fontsize = 20)
    axes[0].text(117, 0.1,'\nQuadrant II', fontsize = 20)
    axes[0].text(217, 0.1,'\nQuadrant III', fontsize = 20)
    axes[0].text(322, 0.1,'\nQuadrant IV', fontsize = 20)
    
    for i, ax in enumerate(axes): 
        ax.tick_params(labelsize = 16, labelright = True)
        ax.xaxis.set_major_locator(MultipleLocator(97))
        ax.minorticks_on()
        ax.grid(which = 'both', linestyle = '-', linewidth = '1', color = 'dimgrey')
        ax.grid(which = 'minor', linestyle = ':', linewidth = '1', color = 'grey')
        
    plt.tight_layout()
    plt.xticks(fontsize = 12)
    plt.yticks(fontsize = 12)
    plt.tick_params(labelsize = 16, labelright = True)
    plt.pause(0.01)
    

def goAndSaveIndividualPlot(sineWave: pd.Series,
                            curveToObserve: pd.Series,
                            savePath: str) -> None: # technically returns an image but couldn't find much information online about type hinting for this case.
    
    '''
    Function used for creating a plot showing both the sine wave, and the output from the matrixMash function computed over the sine wave.
    Stores the plot in a folder (defined by the user) in numerical order (1.png, 2.png etc.). 
      
    Parameters
    ----------   
    sineWave : 
        The sineWave generated. Dependent variable.
    curveToObserve : pd.Series
        Output data from matrixMash function. Independent variable.
    savePath : str
        Defines where the files are to be saved. 
    '''

    fig, axes = plt.subplots(2,1, figsize=[14.275,14.275], sharex=True)

    axes[0].plot(pd.DataFrame(sineWave), color = 'black',linewidth = 1)
    axes[1].plot(curveToObserve, color = 'black',linewidth = 1)

    for i, ax in enumerate(axes): 
        ax.tick_params(labelsize = 16, labelright = True)
        ax.xaxis.set_major_locator(MultipleLocator(len(sineWave)/10))
        ax.minorticks_on()
        ax.grid(which = 'both', linestyle = '-', linewidth = '1', color = 'dimgrey')
        ax.grid(which = 'minor', linestyle = ':', linewidth = '1', color = 'grey')
        
    plt.tight_layout()
    plt.xticks(fontsize = 12)
    plt.yticks(fontsize = 12)
    plt.tick_params(labelsize = 16, labelright = True)
    #plt.pause(0.01) # add this line to see the charts inline
    
    imageCount = 0
    while True:
        imageCount +=1
        filePathForImage = "{}{}.png".format(savePath, imageCount)
        if os.path.exists(filePathForImage):
            continue
        fig.savefig(filePathForImage)
        break
    

def goAndSavePlots(subsections: list[list],
                   savePath: str) -> None:
            
    '''
    Function used to implement the goAndSaveIndividualPlot() function for the entirety of the sine wave.
    It could make sense to use concurrency here, but do be warned, it becomes quite the headache with starmap, tqdm, and matplotlib.pyplot.
    
    Parameters
    ----------   
    subsections : list[list]
        The batched sections of the sine wave.
    savePath : str
        Defines where the files are to be saved. 
    '''    
    
    for i, j in tqdm(enumerate(subsections), total = len(subsections)):
        goAndSaveIndividualPlot(j,  matrixMash(j), savePath)
        

sineWave = sine(numberOfHertz = 780,
                sineFrequency = 2,
                sampleSize = 780,
                wobbleType = None,
                wobbleDegree = 100)

subsections = batcher(sineWave,
                      subframeLength = 90,
                      gapToNextFrame = 1)

complexPlaneAndSinePlot(subsections)

'''This here below is how you would use the goAndSavePlots() function to save the plots to a folder on your desktop.'''
#savePath = '/Users/claytonduffin/Desktop/subDir/'
#goAndSavePlots(subsections, savePath)
