from enum import Enum


class Bid:
    def __init__(self, bidder_id, amount):  # The amount is the max bid for comissions
        self.bidder_id = bidder_id
        self.amount = amount


# TODO: Have an offline bid function
# TODO: Add the function to get the reputation of the user from the auction house
class Item:
    def __init__(self, name, id, min_bid=0, increment=50):
        self.name = name
        self.id = id
        self.min_bid = min_bid
        self.max_bid = min_bid  # this will be updated if a new bid has a max bid(offline user)
        self.current_bid = self.min_bid - increment
        self.increment = increment
        self.commissions: [Bid] = []
        self.bids: [Bid] = []

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

    def add_commission(self, bid):
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
        self.name = name
        self.id = id
        self.reputation: Reputation = reputation
        # self.budget = 1000 # default budget for later to make sure the user has a budget
        print(f"User {self.name} created with reputation {self.reputation.name}")

    # def bid(self, item, amount):
    #     if amount <= self.reputation.value[1]:  # and amount <= self.budget:
    #         self.bids.append(Bid(item, amount))
    #         return True
    #     else:
    #         return False



    def __str__(self):
        return f"{self.name} ({self.id}) has a reputation of {self.reputation.name}"


class AuctionHouse:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.users: [User] = []
        self.items: [Item] = []
        self.known_auction_houses: [AuctionHouse] = []

    def get_reputation_from_auction_houses(self, name):
        # get reputation from auction houses
        # If the user is known by other auction houses we can return a better reputation for the user, otherwise return the default reputation
        for auction_house in self.known_auction_houses:
            for user in auction_house.users:
                if user.name == name:
                    print(f"Found user {user.name} in {auction_house.name} with reputation: {user.reputation}")
                    return user.reputation

        return Reputation.UNKNOWN

    def add_known_auction_house(self, auction_house):
        self.known_auction_houses.append(auction_house)

    def add_user(self, user):
        if user.reputation == Reputation.UNKNOWN:
            user.reputation = self.get_reputation_from_auction_houses(user.name)
        self.users.append(user)
        print(f"Added user {user.name} to {self.name}")


    def add_item(self, item):
        self.items.append(item)

    def start_auction(self, item):
        pass

def test(auction_house):
    auction_house.add_user(User("Alice", "A"))
    auction_house.add_user(User("Bob", "B"))
    auction_house.add_user(User("Cecile", "C"))

    auction_house.add_item(Item("Old Beer", "1", 500, 50))

    # Adds commission of 500 from A
    auction_house.items[0].add_commission(Bid("A", 500))
    auction_house.items[0].add_commission(Bid("B", 700))
    auction_house.items[0].compute_commissions()

    # Add online bids
    auction_house.items[0].compute_auction()

    # Compute winner
    winner = auction_house.items[0].compute_winner()
    print(f"The winner is {winner.bidder_id} with a bid of {winner.amount} for the item {auction_house.items[0].name}")


if __name__ == "__main__":
    auction_house = AuctionHouse("Auction House 1", "1")
    auction_house2 = AuctionHouse("Auction House 2", "2")

    # Auction house one can query the reputation of users from auction house 2
    auction_house.add_known_auction_house(auction_house2)
    auction_house2.add_user(User("Alice", "A", Reputation.REPUTABLE))
    auction_house2.add_user(User("Bob", "B", Reputation.KNOWN))

    #
    test(auction_house)
