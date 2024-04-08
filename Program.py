from enum import Enum


class Bid:
    def __init__(self, bidder_id, amount, max_bid=None): # We only have max bids for offline users
        self.bidder_id = bidder_id
        self.amount = amount
        self.max_bid = amount

# TODO: Have an offline bid function
# TODO: Add the function to get the reputation of the user from the auction house
class Item:
    def __init__(self, name, id, min_bid=0, increment=50):
        self.name = name
        self.id = id
        self.min_bid = min_bid
        self.max_bid = min_bid # this will be updated if a new bid has a max bid(offline user)
        self.current_bid = self.min_bid - increment
        self.increment = increment
        self.offline_bids: [Bid] = []
        self.bids: [Bid] = []

    # This works for online bids but a new functino should be done for offline bids
    def add_bid(self, bid):
        if bid.amount >= self.current_bid + self.increment:  # Check if the bid is higher than the minimum bid
            if bid.bidder_id in [b.bidder_id for b in self.bids]:  # Check if the bidder already has a bid
                for b in self.bids:
                    if b.bidder_id == bid.bidder_id:
                        if bid.amount > b.amount:
                            b.amount = bid.amount
                            self.current_bid = self.current_bid + self.increment

            else:
                self.bids.append(bid)
            print(f"{bid.bidder_id} has bid {bid.amount} on {self.name}")
            return True  # Bid successfully added
        else:
            return False  # Bid invalid

    def compute_winner(self):
        if len(self.bids) > 0:
            return max(self.bids, key=lambda x: x.amount)  # Get the highest bid
        else:
            return None


class Reputation(Enum):
    REPUTABLE = (5, 10000)
    KNOWN = (3, 5000)
    UNKNOWN = (1, 1000)


class User:
    def __init__(self, name, id, reputation=Reputation.UNKNOWN):
        self.name = name
        self.id = id
        self.reputation: Reputation = reputation
        # self.budget = 1000 # default budget for later to make sure the user has a budget

    # def bid(self, item, amount):
    #     if amount <= self.reputation.value[1]:  # and amount <= self.budget:
    #         self.bids.append(Bid(item, amount))
    #         return True
    #     else:
    #         return False

    def get_reputation_from_auction_houses(self, name):
        # get reputation from auction houses
        # If the user is known by other auction houses we can return a better reputation for the user, otherwise return the default reputation
        return Reputation.UNKNOWN

    def __str__(self):
        return f"{self.name} has a budget of {self.budget} and has made the following bids: {self.bids}"


class AuctionHouse:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.users: [User] = []
        self.items: [Item] = []

    def add_user(self, user):
        self.users.append(user)

    def add_item(self, item):
        self.items.append(item)

    def start_auction(self, item):
        pass


    def test(self):
        self.add_user(User("Alice", "A"))
        self.add_user(User("Bob", "B"))
        self.add_user(User("Cecile", "C"))

        self.add_item(Item("Old Beer", "1", 500, 50))


        self.items[0].add_bid(Bid("A", 500))
        self.items[0].add_bid(Bid("B", 550))
        self.items[0].add_bid(Bid("C", 600)) # Online user input
        self.items[0].add_bid(Bid("B", 650)) # Auctionhouse automatic
        self.items[0].add_bid(Bid("C", 700)) # Online user bid should fail because B has prio
        self.items[0].add_bid(Bid("B", 700)) # this is the bid that should be accepted
        self.items[0].add_bid(Bid("C", 750)) # Online user bids, and is accepted
        print(f"The winner is {self.items[0].compute_winner().bidder_id}")

if __name__ == "__main__":
    auction_house = AuctionHouse("Auction House 1", "1")
    auction_house.test()
