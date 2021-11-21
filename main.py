import decimal, json, time, os, discordWH
from decimal import Decimal
from web3 import Web3
from dotenv import load_dotenv
# import twitter

load_dotenv()
check_delay_sec = int(os.getenv('CHECK_DELAY_SEC'))

cauldrons = json.loads(open("Cauldrons.json", 'r').read()) #Loads Cauldrons.json as a nested dic
settings = json.loads(open("Settings.json", 'r').read()) #Loads Chains Info

def checkTreshold(previous_amount, amount, treshold):
    if amount - previous_amount > treshold: #check if the increase is > treshold
        if previous_amount == 0: #if previousAmount is "pure" 0, we send message
            return True
        elif amount - previous_amount > Decimal(0.15) * previous_amount: #check wether the increase is at least a 30% increase
            return True
        else:
            return False

def  getMIMAmount(mim_address, cauldron):
    mim_amount = bentobox.functions.balanceOf(mim_address, cauldron).call()
    mim_amount = w3.fromWei(mim_amount, 'ether')
    return Decimal(mim_amount)

while True:
    for chain in settings.keys(): #Go though each chain
        w3 = Web3(Web3.HTTPProvider(settings[chain]['RPC'])) #Network RPC
        bb_address = w3.toChecksumAddress(settings[chain]['bentobox']) #BentoBox Contract Address
        MIM_contract_address=w3.toChecksumAddress(settings[chain]['MIM']) #MIM Contract Address
        bb_ABI = json.load(open('BentoBoxV1.json', 'r')) #BentoBox ABI load, from BentoBoxV1.json
        bentobox = w3.eth.contract(address=bb_address, abi=bb_ABI)

        for tokens in cauldrons.keys(): #Go through each Cauldron entry
            if cauldrons[tokens]['chain'] == chain: #Check wether the Cauldron entry is on the chain we are working with 

                previous_amount = Decimal(cauldrons[tokens]['previous_amount'])
                amount = getMIMAmount(MIM_contract_address, w3.toChecksumAddress(cauldrons[tokens]['address'])) #Gets MIM available for the cauldron
                threshold = Decimal(settings[chain]['threshold'])
                
                print("%s on %s:" %(tokens, chain))
                # print("Old amount : ", cauldrons[tokens]['previous_amount'])
                # print("New amount : ", amount)
                print("Current MIMs available: ", amount)
                print("-----")

                if checkTreshold(previous_amount, amount, threshold): 
                    try:
                        discordWH.sendMessage(tokens, amount, cauldrons, settings, chain) #Send discord msg
                    except:
                        print("error sending discord message")
                    #twitter.tweet(tokens, amount, settings, chain)

                cauldrons[tokens]['previous_amount'] = str(amount) #Store amount as Previous_amount
    
    # Update previous amount
    json.dump(cauldrons, open("Cauldrons.json", 'w'), indent=4, sort_keys=True)

    # Sleep before next run
    time.sleep(check_delay_sec)
