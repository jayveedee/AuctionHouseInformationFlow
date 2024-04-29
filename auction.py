from enum import Enum

# Security Lattice: Based on the Myers-Liskov Approach
# {B: {B,A}, C: {C,A}} - Security label for new bid data
# {A: {A}} - Security label for all bidder data (Auction House only)
# {S: {S}} - Security label for the bidder database (Secondary Auction House only)
# {B: {B,A}} - Security label for current highest bid data


class Bid:
    def __init__(self, bidder_id, amount):  # The amount is the max bid for comissions
        self.bidder_id = bidder_id # label: {B: {B,A}, C: {C,A}}
        self.amount = amount # label: {B: {B,A}, C: {C,A}}


# TODO: Have an offline bid function
# TODO: Add the function to get the reputation of the user from the auction house
class Item:
    def __init__(self, name, id, min_bid=0, increment=50):
        self.name = name # label: {A: {A}}
        self.id = id # label: {A: {A}}
        self.min_bid = min_bid # label: {A: {A}}
        self.max_bid = min_bid # label: {A: {A}} , {B: {B,A}}  
        self.current_bid = self.min_bid - increment # label: {A: {A}} , {B: {B,A}}
        self.increment = increment # label: {A: {A}}
        self.commissions: [Bid] = [] # label: {A: {A}}
        self.bids: [Bid] = [] # label: {A: {A}} , {B: {B,A}}

    # This works for online bids but a new functino should be done for offline bids
    def add_bid(self, bid, auction_house_bid=False):
        if bid.amount >= self.current_bid + self.increment:  # Check if the bid is higher than the minimum bid
            if bid.bidder_id in [b.bidder_id for b in self.bids]:  # Check if the bidder already has a bid
                for b in self.bids:
                    if b.bidder_id == bid.bidder_id:
                        if bid.amount > b.amount:
                            b.amount = bid.amount
                            if auction_house_bid:
                                self.current_bid = bid.amount

            else:
                self.bids.append(bid)

            if not auction_house_bid:
                self.current_bid = bid.amount

            print_string = f"{bid.bidder_id} bids {self.current_bid} kr on {self.name}"
            if auction_house_bid:
                print_string = f"Auction house bids for {bid.bidder_id}: {self.current_bid} Kr on {self.name}"

            print(print_string)

            # Check if highest offline bid is higher, if so print that the auction house actually bid that ofr them
            print_bid_for_commission = False
            if self.current_bid + self.increment < self.bids[0].amount and not auction_house_bid:
                print_bid_for_commission = True
                self.current_bid += self.increment

            # If the same amount is bid the offline bid wins
            elif self.current_bid == self.bids[0].amount and not auction_house_bid:
                print_bid_for_commission = True

            if print_bid_for_commission:
                print(
                    f"Auction house bids for {self.bids[0].bidder_id}: {self.current_bid} Kr on {self.name}")

            return True  # Bid successfully added
        else:
            return False  # Bid invalid

    def add_commission(self, bid): # label: {C: {C,A}} 
        self.commissions.append(bid)

    def compute_commissions(self):
        # Get the highest bid
        if len(self.commissions) > 0:
            sorted_commissions = sorted(self.commissions, key=lambda x: x.amount)
            # Get the highest commission
            highest_commission = sorted_commissions[-1]
            # Get the second highest commission, so we can calculate the starting bid
            if len(sorted_commissions) > 1:
                self.current_bid = sorted_commissions[-2].amount + self.increment

            # Add the highest bidder, we know that this bid is the only offline bid (as they are computed beforehand)
            self.add_bid(highest_commission, auction_house_bid=True)

    def compute_auction(self):
        # Add online bids
        while True:
            bidder_id = input("Enter Bidder ID (or 'x' to exit): ")
            if bidder_id == 'x':
                break
            self.add_bid(Bid(bidder_id, int(input("Enter bid amount: "))))

    def compute_winner(self):
        print("Going once, going twice, sold!")
        if len(self.bids) > 0:
            # Offline bidders win be default
            if self.bids[0].amount >= self.current_bid:
                return self.bids[0]
            else:
                return max(self.bids, key=lambda x: x.amount)  # Get the highest bid
        else:
            return None


class Reputation(Enum):
    REPUTABLE = (5, 10000)
    KNOWN = (3, 5000)
    UNKNOWN = (1, 1000)


class User:
    def __init__(self, name, id, reputation=Reputation.UNKNOWN):
        self.name = name # label: {S: {S}} , {A: {A}} 
        self.id = id # label: {S: {S}} , {A: {A}} 
        self.reputation: Reputation = reputation # label: {S: {S}} , {A: {A}} 
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
        self.name = name # label: {A: {A}}
        self.id = id # label: {A: {A}}
        self.users: [User] = [] # label: {A: {A}}
        self.items: [Item] = [] # label: {A: {A}}

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

        # Adds commission of 500 from A
        self.items[0].add_commission(Bid("A", 500))
        self.items[0].add_commission(Bid("B", 700))
        self.items[0].compute_commissions()

        # Add online bids
        self.items[0].compute_auction()

        # Compute winner
        winner = self.items[0].compute_winner()
        print(f"The winner is {winner.bidder_id} with a bid of {winner.amount} for the item {self.items[0].name}")


if __name__ == "__main__":
    auction_house = AuctionHouse("Auction House 1", "1")
    auction_house.test()