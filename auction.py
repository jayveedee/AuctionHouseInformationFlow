from enum import Enum

# Security Lattice: Based on the Myers-Liskov Approach
# {B: {B,A}, C: {C,A}} - Security label for new bid data
# {A: {A}} - Security label for all bidder data (Auction House only)
# {S: {S}} - Security label for the bidder database (Secondary Auction House only)
# {B: {B,A}} - Security label for current highest bid data

class Bid:
    def __init__(self, bidder_id, amount):  # The amount is the max bid for commissions
        self.bidder_id = bidder_id  # label: {B: {B,A}, C: {C,A}}
        self.amount = amount  # label: {B: {B,A}, C: {C,A}}

class Item:
    def __init__(self, name, id, min_bid=0, increment=50):
        self.name = name  # label: {A: {A}}
        self.id = id  # label: {A: {A}}
        self.min_bid = min_bid  # label: {A: {A}}
        self.max_bid = min_bid  # label: {A: {A}}, {B: {B,A}}
        self.current_bid = self.min_bid - increment  # label: {A: {A}}, {B: {B,A}}
        self.increment = increment  # label: {A: {A}}
        self.commissions = []  # label: {C: {C,A}}
        self.bids = []  # label: {B: {B,A}, C: {C,A}}

    def add_bid(self, bid, auction_house_bid=False):
        if bid.amount >= self.current_bid + self.increment:
            if bid.bidder_id in [b.bidder_id for b in self.bids]:
                for b in self.bids:
                    if b.bidder_id == bid.bidder_id:
                        if bid.amount > b.amount:
                            b.amount = bid.amount
                            if auction_house_bid:
                                self.current_bid = bid.amount  # label: {A: {A}}, {B: {B,A}}

            else:
                self.bids.append(bid)  # label: {B: {B,A}, C: {C,A}}

            if not auction_house_bid:
                self.current_bid = bid.amount  # label: {A: {A}}, {B: {B,A}}

            print_string = f"{bid.bidder_id} bids {self.current_bid} kr on {self.name}"
            if auction_house_bid:
                print_string = f"Auction house bids for {bid.bidder_id}: {self.current_bid} Kr on {self.name}"

            print(print_string)  # label: {⊥}

            return True  # label: {⊥}
        else:
            return False  # label: {⊥}

    def add_commission(self, bid):
        self.commissions.append(bid)  # label: {C: {C,A}}

    def compute_commissions(self):
        if len(self.commissions) > 0:
            sorted_commissions = sorted(self.commissions, key=lambda x: x.amount)
            highest_commission = sorted_commissions[-1]
            if len(sorted_commissions) > 1:
                self.current_bid = sorted_commissions[-2].amount + self.increment  # label: {A: {A}}, {B: {B,A}}
            self.add_bid(highest_commission, auction_house_bid=True)  # label: {B: {B,A}, C: {C,A}}

    def compute_auction(self):
        while True:
            bidder_id = input("Enter Bidder ID (or 'x' to exit): ")  # label: {⊥}
            if bidder_id == 'x':
                break
            self.add_bid(Bid(bidder_id, int(input("Enter bid amount: "))))  # label: {B: {B,A}, C: {C,A}}

    def compute_winner(self):
        print("Going once, going twice, sold!")  # label: {⊥}
        if len(self.bids) > 0:
            highest_bid = max(self.bids, key=lambda x: x.amount)
            return highest_bid  # label: {B: {B,A}, C: {C,A}}
        else:
            return None  # label: {⊥}

class Reputation(Enum):
    REPUTABLE = (5, 10000)  # label: {⊥}
    KNOWN = (3, 5000)  # label: {⊥}
    UNKNOWN = (1, 1000)  # label: {⊥}

class User:
    def __init__(self, name, id, reputation=Reputation.UNKNOWN):
        self.name = name  # label: {S: {S}}, {A: {A}}
        self.id = id  # label: {S: {S}}, {A: {A}}
        self.reputation = reputation  # label: {S: {S}}, {A: {A}}

    def __str__(self):
        return f"{self.name} ({self.id}) has a reputation of {self.reputation.name}"  # label: {⊥}

class AuctionHouse:
    def __init__(self, name, id):
        self.name = name  # label: {A: {A}}
        self.id = id  # label: {A: {A}}
        self.users = []  # label: {A: {A}}
        self.items = []  # label: {A: {A}}
        self.known_auction_houses = []  # label: {A: {A}}

    def add_known_auction_house(self, auction_house):
        self.known_auction_houses.append(auction_house)  # label: {A: {A}}

    def add_user(self, user):
        if user.reputation == Reputation.UNKNOWN:
            user.reputation = self.get_reputation_from_auction_houses(user.name)  # label: {S: {S}}, {A: {A}}
        self.users.append(user)  # label: {A: {A}}

    def add_item(self, item):
        self.items.append(item)  # label: {A: {A}}

    def start_auction(self, item):
        pass  # label: {⊥}

    def get_reputation_from_auction_houses(self, name):
        for auction_house in self.known_auction_houses:
            for user in auction_house.users:
                if user.name == name:
                    print(f"Found user {user.name} in {auction_house.name} with reputation: {user.reputation}")  # label: {⊥}
                    return user.reputation
        return Reputation.UNKNOWN  # label: {⊥}

def main():
    auction_house = AuctionHouse("Auction House 1", "1")
    auction_house2 = Auction House("Auction House 2", "2")
    auction_house.add_known_auction_house(auction_house2)
    auction_house2.add_user(User("Alice", "A", Reputation.REPUTABLE))
    auction_house2.add_user(User("Bob", "B", Reputation.KNOWN))
    auction_house.add_user(User("Alice", "A"))
    auction_house.add_user(User("Bob", "B"))
    auction_house.add_user(User("Cecile", "C"))
    auction_house.add_item(Item("Old Beer", "1", 500, 50))
    auction_house.items[0].add_commission(Bid("A", 500))
    auction_house.items[0].add_commission(Bid("B", 700))
    auction_house.items[0].compute_commissions()
    auction_house.items[0].compute_auction()
    winner = auction_house.items[0].compute_winner()
    print(f"The winner is {winner.bidder_id} with a bid of {winner.amount} for the item {auction_house.items[0].name}")  # label: {⊥}

if __name__ == "__main__":
    main()
