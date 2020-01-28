#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 18:46:07 2020

@author: Dennis Gross
"""
import pandas as pd
from pysmt.shortcuts import Symbol, Int, Times, Plus, And, Or, GE, LE, Equals, get_model
from pysmt.typing import INT
import sys



def nutrition_calculator(dishes, number_of_calories, number_of_dishes, disabled_dishes = [], alpha = 100):
    '''
        This method creates a dish plan based on the daily allowed calories
        and the number of dishes.
        Args:
            dishes, pandas data frame. Each row looks like this: (dish name, calories, proteins).
            number_of_calories, the daily number of calories.
            number_of_dishes, the daily number of dishes.
            disabled_dishes, list of row indizes from dishes which are not allowed in the current calculation.
            alpha, the allowed deviation of calories
        Returns:
            row indizes from dishes data frame. These dishes can be eaten today.
    '''
    # Upper and lower calory boundaries
    calories_upper_boundary = Int(int(number_of_calories + alpha))
    calories_lower_boundary = Int(int(number_of_calories - alpha))
    # List of SMT variables
    x = []
    # List of all x_i * d_i2
    x_times_calories = []
    # List of all x_i € {0,1}
    x_zero_or_one = []
    # List of disabled dishes
    x_disabled_sum = []
    for index, row in dishes.iterrows():
        x.append(Symbol('x' + str(index), INT))
        # x_i * d_i2
        x_times_calories.append(Times(x[-1], Int(row.calories)))
        # x_i € {0,1}
        x_zero_or_one.append(Or(Equals(x[-1], Int(0)), Equals(x[-1], Int(1))))
        # Disable potential dishes
        if index in disabled_dishes:
            x_disabled_sum.append(x[-1])
    x_times_calories_sum = Plus(x_times_calories)
    x_sum = Plus(x)
    if len(x_disabled_sum) == 0:
        x_disabled_sum = Int(0)
    else:
        x_disabled_sum = Plus(x_disabled_sum)
    formula = And(
        [
            # Makes sure that our calories are above the lower boundary
            GE(x_times_calories_sum, calories_lower_boundary),
            # Makes sure that our calories are below the upper boundary
            LE(x_times_calories_sum, calories_upper_boundary),
            # Makes sure that we get number_of_dishes dishes per day
            Equals(x_sum, Int(int(number_of_dishes))),
            # Makes sure that we don't use the disabled dishes
            Equals(x_disabled_sum, Int(0)),
            # Makes sure that each dish is maximal used once
            And(x_zero_or_one)
        ]
    )
    # SMT solving
    model = get_model(formula)
    # Get indizes
    if model:
        result_indizes = []
        for i in range(len(x)):
            if(model.get_py_value(x[i]) == 1):
                result_indizes.append(i)
        return result_indizes
    else:
        return None

def print_dishes(dishes, dish_indizes):
    '''
        This method prints the dishes for today.
        Args:
            dishes, pandas data frame. Each row looks like this: (dish name, calories, proteins).
            dish_indizes, List of dish indizes
    '''
    for index, row in dishes.iterrows():
        if index in dish_indizes:
            print(row.name, 'has got', row.calories,"and",row.proteins,"proteins")



if __name__ == '__main__':
    # Read dish data set
    dishes = pd.read_csv("dishes.csv")
    # Check if the number of arguments is correct
    if len(sys.argv) != 3:
        raise Exception("Correct command: PYTHON calculator.py NUMBER_OF_CALORIES NUMBER_OF_DISHES")
    # number of daily calories
    try:
        number_of_calories = int(sys.argv[1])
    except:
        raise Exception("First argument has to be an integer")
    # number of dishes today
    try:
        number_of_dishes = int(sys.argv[2])
    except:
        raise Exception("Second argument has to be an integer")
    indizes = nutrition_calculator(dishes,number_of_calories, number_of_dishes)
    if indizes != None:
        print_dishes(dishes, indizes)
    else:
        print("No Solution")
