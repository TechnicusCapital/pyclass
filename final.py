import random
import seaborn as sns
import matplotlib.pyplot as plt

def martingale(bankroll):
    bet = 20
    pockets = ["Red"] * 18 + ["Black"] * 18 + ["Green"] * 2
    bankroll_history = []
    run = []
    inBet = False
    while 0 < bankroll < 1000:
        if bet > bankroll:
            bet = bankroll

        roll = random.choice(pockets)
        run.append(roll)

        if len(run) > 8:
            del run[0]
        cond = all(e == "Red" for e in run[:-1])

        if cond and inBet == False:
            inBet = True

        if cond and inBet == True:
            bankroll -= bet
            bet *= 2
        
        if cond == False and inBet == True:
            bankroll += bet
            bet = 20
            inBet = False
        
        # if bankroll <= 0:
        #     bankroll += 50
        
        bankroll_history.append(bankroll)
        #print(bankroll)
    return bankroll_history
    
martingale(bankroll=100)

sns.set(rc={'figure.figsize':(11.7,8.27)})
# for i in range(4):
plt.plot(martingale(bankroll=100), linewidth=2)
    
plt.xlabel("Number of Games", fontsize=18, fontweight="bold")
plt.ylabel("Bankroll", fontsize=18, fontweight="bold")
plt.xticks(fontsize=16, fontweight="bold")
plt.yticks(fontsize=16, fontweight="bold")
plt.title("Bankroll Over Time", fontsize=22, fontweight="bold")
plt.show()