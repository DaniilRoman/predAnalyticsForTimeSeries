import time
from threading import Thread

from statsmodels.tsa.seasonal import seasonal_decompose
import numpy as np

from src.processing import DataHolder


class SeasonalPeriod:

    def __init__(self, dataStore: DataHolder, left: int = 10, right: int = 80):
        self.dataStore = dataStore
        self.left = left
        self.right = right
        self.period = 40

    def calculatePeriodInWhile(self):
        while True:
            if self.dataStore.seasonal != []:
                self.fastCalculateSeasonalPeriod()
            time.sleep(self.dataStore.delay)

    def fastCalculateSeasonalPeriod(self, depth: int = 10, window: int = 5):
        series: list = self.dataStore.seasonal.copy()
        length: int = len(series)
        midleSeries: int = int(length / 2)
        bestPeriod = self.left
        prevBestPeriod = bestPeriod - 1
        bestError = 200           # REFACTOR
        seriesForCheck = series[midleSeries:]
        bestSeasonal = seriesForCheck
        count = 0

        left = self.left
        right = self.right
        midle = int((right - left) / 2)

        for i in range(depth):
            #         if(bestPeriod == prevBestPeriod): break
            leftMidle = left + int((midle - left) / 2)
            rightMidle = midle + int((right - midle) / 2)

            resultLeft = seasonal_decompose(series, model='aditive', freq=leftMidle)
            resultRight = seasonal_decompose(series, model='aditive', freq=rightMidle)

            seasonalLeft = resultLeft.seasonal[midleSeries:]
            seasonalLeft = seasonalLeft + abs(min(seasonalLeft))
            seasonalRight = resultRight.seasonal[midleSeries:]
            seasonalRight = seasonalRight + abs(min(seasonalRight))
            errorLeft = self.meanAbsolutePercentageError(seriesForCheck, seasonalLeft)
            errorRight = self.meanAbsolutePercentageError(seriesForCheck, seasonalRight)
            # count = count + 1
            #         print("bestPeriod: {}".format(bestPeriod))
            if (errorRight >= errorLeft):
                bestError = errorRight
                prevBestPeriod = bestPeriod
                bestPeriod = rightMidle
                bestSeasonal = resultRight.seasonal
                left = midle
                midle = rightMidle
            else:
                bestError = errorLeft
                prevBestPeriod = bestPeriod
                bestPeriod = leftMidle
                bestSeasonal = resultLeft.seasonal
                right = midle
                midle = leftMidle

        if bestPeriod - window < 0:
            left = self.left
        else:
            left = bestPeriod - window
        if bestPeriod + window > self.right:
            right = self.right
        else:
            right = bestPeriod + window
        for i in range(left, right):
            #         if(bestPeriod == prevBestPeriod): break
            result = seasonal_decompose(series, model='aditive', freq=i)
            seasonal = result.seasonal[midle:]
            seriesForCheck = series[midle:]
            error = self.meanAbsolutePercentageError(seriesForCheck, seasonal)
            count = count + 1
            if (error >= bestError):
                bestError = error
                prevBestPeriod = bestPeriod
                bestPeriod = i
                bestSeasonal = result.seasonal
        # print("Count: {}".format(count))
        print("bestPeriod: {}".format(bestPeriod))
        self.period = bestPeriod
        return bestPeriod, bestError, bestSeasonal

    def fullSearchSeasonalityPeriod(self, series):
        length = len(series)
        midle = int(length / 2)
        seriesForCheck = series[midle:]
        bestPeriod = self.left
        bestError = 200           # REFACTOR
        bestSeasonal = seriesForCheck
        for i in range(self.left, self.right):
            result = seasonal_decompose(series, model='aditive', freq=i)
            seasonal = result.seasonal[midle:]
            error = self.meanAbsolutePercentageError(seriesForCheck, seasonal)
            #         print(error)
            if (error >= bestError):
                bestError = error
                bestPeriod = i
                bestSeasonal = result.seasonal
        self.period = bestPeriod
        return bestPeriod, bestError, bestSeasonal

    def meanAbsolutePercentageError(self, y_true, y_pred):
        return np.mean(np.abs((y_true - y_pred) / y_true)) * 100
