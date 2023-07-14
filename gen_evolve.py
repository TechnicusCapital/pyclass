import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import numpy as np
import mplfinance as mpf
from scipy import stats
from genetic_funcs import reproduce, mutate_string
from timeit import default_timer as timer
import ast

INSAMPLE_START = '2018-01-01'
INSAMPLE_END = '2021-01-01'
OUTSAMPLE_START = INSAMPLE_END
OUTSAMPLE_END = '2023-06-01'
TICKER = 'GLD'


class PatternGenerator:
    def __init__(self, data, size, pattern_length):
        self.data = data
        self.O = pd.Series(dtype='float64')
        self.H = pd.Series(dtype='float64')
        self.L = pd.Series(dtype='float64')
        self.C = pd.Series(dtype='float64')
        self.data['NextDayLogReturn'] = np.log(self.data['Close'].shift(-1) / self.data['Close'])
        self.data = self.data[:-1]
        self.size = size
        self.len = pattern_length

    def random_ohlc(self):
        x = np.random.randint(0, 4)
        idx = np.random.randint(1, self.len + 1)
        switch = ['O', 'H', 'L', 'C']
        a = switch[x]
        return f'{a}[{-idx}]'
    
    def comparator(self):
        x = np.random.randint(0, 2)
        switch = [' > ', ' < ']
        return switch[x]
    
    def generate(self):
        pattern = ''
        for _ in range(self.size):
            a, b, c = self.random_ohlc(), self.comparator(), self.random_ohlc()
            if a == c:
                a, b, c = self.random_ohlc(), self.comparator(), self.random_ohlc()
            pattern = f'{pattern}{a}{b}{c}'
            if _ == self.size - 1:
                break
            pattern += ' and '
        return pattern
    
    # ---- IMPROVE PERFORMANCE HERE (VECTORIZATION?)
    def backtest(self, pattern):
        returns = []
        pattern = pattern.replace('L', 'self.L').replace('H', 'self.H').replace('C', 'self.C').replace('O', 'self.O')
        and_count = pattern.count("and")
        parenthesized_statement = pattern.replace("and", ") and (", and_count)
        pattern = "(" + parenthesized_statement + ")"
        for idx in range(len(self.data)):
            if idx >= self.len:
                data = self.data[idx - (self.len - 1) : idx + 1]
                self.O, self.H, self.L, self.C = data['Open'].values, data['High'].values, data['Low'].values, data['Close'].values
                if eval(pattern):
                    returns.append(self.data['NextDayLogReturn'][idx])
                else:
                    returns.append(0)

        cumreturns = np.exp(np.cumsum(returns))
        cumreturns = cumreturns.tolist()
        return returns, cumreturns

    
    def profit_factor(self, returns):
        pos = 0
        neg = 0

        for r in returns:
            if r > 0:
                pos += r
            elif r < 0:
                neg += r
        
        pf = (pos / abs(neg))
        #print(f'Wins: {pos}\nLosses: {abs(neg)}\nProfit Margin: {pf}')
        if pf < 0: 
            pf = 0
        pf = np.log(pf)
        return pf  
    # ---- TO-DO: Double check for errors
    
    def mRatio(self, returns, cumreturns):
        sum_sq = 0
        max_val = 0.001
        idx = 0
        for r in cumreturns:
            if r > max_val:
                max_val = r
            elif idx > 0 and r != cumreturns[idx - 1]: # ---- Not sure whether to use all returns or just the changes
                x = 100 * ((r/max_val) - 1)
                sum_sq += np.power(x, 2)
            idx += 1

        ui = np.sqrt(sum_sq / len(cumreturns))
        avg_daily_ret = np.mean(returns)
        ann_ret = np.exp((252) * avg_daily_ret) - 1
        upi = (ann_ret - 0.04) / (ui/100)
        #print(f'Annualized Return: {ann_ret}%\nUlcer Index: {ui}')
        return upi        
    
    # Fix breeding system --- Weird error occurs with not filling children.
    def evolver(self, gen: list, p_size: int):
        evolver_timer = timer()
        print('Starting Evolve Timer')
        # Generation 1 Testing
        c_pop = []
        for pat in gen:
            #print('Calculating Martin Ratio...')
            returns, cumreturn = self.backtest(pat)
            trades = len([ret for ret in returns if ret != 0])
            if trades > 5:
                martinR = self.mRatio(returns, cumreturn)
                #print('Martin Ratio Calculated')
            else:
                martinR = 0
            c_pop.append((pat, martinR))
            # sort current population by highest martinR
            c_pop.sort(key=lambda x: x[1], reverse=True)

        #print(f'Current Population: {current_population}\n----')
        # Select the pattern with the highest fitness
        highest_fitness_pattern = c_pop[0]
        highest_fit_pat2 = c_pop[1]
        #print(f'Highest Fitness Pattern: {highest_fitness_pattern}\n----')
        future_population = []
        future_population.append(highest_fitness_pattern[0])
        future_population.append(highest_fit_pat2[0])
        first = future_population[0]
        future_population = future_population[1:]

        fitness_sum = float()
        for each in c_pop:
            fitness_sum += each[1]
        random_sum = np.random.uniform(0, fitness_sum)
        for _ in range(9):
            p1 = ''
            p2 = ''
            selection_sum = 0.00
            for each in c_pop:
                selection_sum += each[1] 
                if selection_sum >= random_sum:
                    if p1 == '':
                        p1 = each[0]
                        c_pop.remove(each)
                    elif p2 == '':
                        p2 = each[0]
                        c_pop.remove(each)
                        break
            c1, c2 = reproduce(p1, p2)
            future_population.extend([c1, c2])



        # Replace NaN values with the replacement value
        future_population = [self.generate() if x == ' and  and ' or x == '' else x for x in future_population]
        
        # Mutate patterns with a 5% chance
        future_population = [mutate_string(each) if np.random.uniform(0, 1) < 0.05 else each for each in future_population]

                
        future_population.insert(0, first)

        evolver_timer_end = timer()
        print(f'Evolver Timer: {evolver_timer_end - evolver_timer}')
        return future_population, highest_fitness_pattern[1], highest_fitness_pattern[0]
    
    def initial_run(self, population_size: int, evolutions: int):
        # Initial Generation
        print('Creating Initial Generation...')
        gen = [self.generate() for _ in range(population_size + 5)]
        # print(f'First Generation: {gen}')
        last_gen = gen

        # Evolutions
        print('Evolving...')
        for i in range(evolutions):
            pop, highMart, pat = self.evolver(last_gen, population_size)
            print(f'Generation # - {i + 1}\nCurrent Martin Ratio: {highMart}\nPattern: {pat}')
            last_gen = pop
            print(last_gen)

        # Test final population
        print('Testing Final Population...')
        fpop = [(pat, self.mRatio(*self.backtest(pat))) if len([ret for ret in self.backtest(pat)[0] if ret != 0]) > 5 else (pat, 0) for pat in last_gen]
        fpop.sort(key=lambda x: x[1], reverse=True)
        final_p = fpop[0][0]
        returns, cumreturn = self.backtest(final_p)
        return returns, cumreturn, final_p

    def uncorrelated_evolver(self, gen: list, p1_returns: list, p_size: int):
        c_pop = []
        for pat in gen:
            returns, cumreturn = self.backtest(pat)
            trades = len([ret for ret in returns if ret != 0])
            if trades > 5:
                correlation = stats.pearsonr(returns, p1_returns)
                martinR = self.mRatio(returns, cumreturn) * (1 - correlation.statistic)
            else:
                martinR = 0
            c_pop.append((pat, martinR))
            # sort current population by highest martinR
            c_pop.sort(key=lambda x: x[1], reverse=True)

        #print(f'Current Population: {current_population}\n----')
        # Select the pattern with the highest fitness
        highest_fitness_pattern = c_pop[0]
        highest_fit_pat2 = c_pop[1]
        #print(f'Highest Fitness Pattern: {highest_fitness_pattern}\n----')
        future_population = []
        future_population.append(highest_fitness_pattern[0])
        future_population.append(highest_fit_pat2[0])
        first = future_population[0]
        future_population = future_population[1:]

        fitness_sum = float()
        for each in c_pop:
            fitness_sum += each[1]
        random_sum = np.random.uniform(0, fitness_sum)
        for _ in range(round((p_size/2) - 1)):
            p1 = ''
            p2 = ''
            selection_sum = float()
            for each in c_pop:
                selection_sum += each[1] 
                if selection_sum >= random_sum:
                    if p1 == '':
                        p1 = each[0]
                        c_pop.remove(each)
                    else:
                        p2 = each[0]
                        c_pop.remove(each)
                        break
            c1, c2 = reproduce(p1, p2)
            future_population.append(c1)
            future_population.append(c2)


        # Replace NaN values with the replacement value
        for i in range(len(future_population)):
            if future_population[i] == ' and  and ':
                future_population[i] = p.generate()

        
        # Mutate patterns with a 5% chance
        for each in future_population:
            prob = np.random.uniform(0, 1)
            if prob < 0.05:
                future_population[future_population.index(each)] = mutate_string(each)
        future_population.insert(0, first)
        return future_population, highest_fitness_pattern[1], highest_fitness_pattern[0]
    
    def uncorrelated_run(self, population_size: int, evolutions: int, p1_returns: list):
        g = []
        for _ in range(population_size):
            pattern = self.generate()
            g.append(pattern)
        print(f'First Generation: {g}')
        last_g = g

        # Evolutions
        for i in range(evolutions):
            pop, highMart, pat = self.uncorrelated_evolver(last_g, p1_returns, population_size)
            print(f'Generation # - {i + 1}\nCurrent Martin Ratio: {highMart}\nPattern: {pat}')
            last_g = pop

        # Test final population
        fpop = []
        for pat in last_g:
            returns, cumreturn = self.backtest(pat)
            trades = len([ret for ret in returns if ret != 0])
            if trades > 5:
                martinR = self.mRatio(returns, cumreturn)
            else:
                martinR = 0
            fpop.append((pat, martinR))
            # sort current population by highest martinR
        fpop.sort(key=lambda x: x[1], reverse=True)
        final_p = fpop[0][0]
        returns, cumreturn = self.backtest(final_p) # <--- Should be saving this earlier
        return returns, cumreturn, final_p


data = yf.download(TICKER, start=INSAMPLE_START, end=INSAMPLE_END)
p = PatternGenerator(data, 3, 3)

returns, cumreturn, final_p = p.initial_run(population_size=20, evolutions=8)

returns2, cumreturn2, final_p2 = p.uncorrelated_run(population_size=20, evolutions=8, p1_returns=returns)
print(f'Correlation: {stats.pearsonr(returns, returns2)}')

returns3, cumreturn3, final_p3 = p.uncorrelated_run(population_size=20, evolutions=8, p1_returns=returns2)
print(f'Correlation: {stats.pearsonr(returns3, returns2)}')

returns4, cumreturn4, final_p4 = p.uncorrelated_run(population_size=20, evolutions=8, p1_returns=returns3)
print(f'Correlation: {stats.pearsonr(returns3, returns4)}')

returns5, cumreturn5, final_p5 = p.uncorrelated_run(population_size=20, evolutions=8, p1_returns=returns4)
print(f'Correlation: {stats.pearsonr(returns4, returns5)}')


# print(f'{final_p}\n{final_p2}\n{final_p3}\n{final_p4}\n{final_p5}')







# # ---- Plot the final population returns
# x = range(len(cumreturn))
# plt.plot(x, cumreturn)

# # Add labels and title
# plt.xlabel('X-axis')
# plt.ylabel('Y-axis')
# plt.title(f'In-Sample Martin Ratio: {fpop[0][1]}')
# plt.show()

# ---- OOS Testing
patterns = [final_p, final_p2, final_p3, final_p4, final_p5]

newData = yf.download(TICKER, start=OUTSAMPLE_START, end=OUTSAMPLE_END)
f = PatternGenerator(newData, 3, 3)

for pattern in patterns:
    oos_return, oos_cumreturn = f.backtest(pattern)
    martinR2 = f.mRatio(oos_return, oos_cumreturn)
    x2 = range(len(oos_cumreturn))
    plt.plot(x2, oos_cumreturn)

    # Add labels and title
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title(f'Out Sample Martin Ratio: {martinR2}')
    plt.show()