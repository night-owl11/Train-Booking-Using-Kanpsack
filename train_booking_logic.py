# train_booking_logic.py

TOTAL_SEATS = 100
# OVERBOOK_PERCENTAGE = 0.10 # Removed overbooking
CANCELLATION_FEE_PERCENTAGE = 0.20

STATIONS = ["A", "B", "C", "D"]

# Global state variables (Knapsack Capacity and Profit/Revenue)
# Initial capacity is now strictly TOTAL_SEATS
current_total_seats = TOTAL_SEATS
current_total_revenue = 0.0
next_group_id = 1

class Group:
    """Represents a booking group (Knapsack Item)."""
    def __init__(self, route, members, fare_per_section, group_id=None):
        global next_group_id
        self.id = group_id if group_id is not None else next_group_id
        if group_id is None:
            next_group_id += 1
            
        self.route = route
        self.from_station = route[0]
        self.to_station = route[1]
        self.members = int(members)
        self.total_fare = self._calculate_fare(fare_per_section)
        self.is_booked = False

    def _get_station_index(self, station):
        try:
            return STATIONS.index(station)
        except ValueError:
            return -1

    def _calculate_fare(self, fare_per_section):
        from_index = self._get_station_index(self.from_station)
        to_index = self._get_station_index(self.to_station)
        
        if from_index == -1 or to_index == -1 or from_index >= to_index:
            # Simple error handling for invalid route
            sections = 0
        else:
            sections = to_index - from_index
            
        self.sections = sections
        return fare_per_section * sections * self.members

    def __lt__(self, other):
        """Used for sorting (Greedy choice). Sort by highest fare first."""
        if self.total_fare != other.total_fare:
            return self.total_fare > other.total_fare
        return self.members < other.members

# def apply_overbooking_capacity(base_capacity): # Removed
#     """Calculates the overbooked capacity (Knapsack capacity W)."""
#     return int(base_capacity * (1.0 + OVERBOOK_PERCENTAGE))

def allocate_seats(groups, fare_per_section):
    """
    Implements the Knapsack-like Greedy Allocation. Capacity is fixed at TOTAL_SEATS.
    Returns a tuple: (allocated_groups, waiting_groups, total_revenue, remaining_seats)
    """
    global current_total_seats, current_total_revenue
    
    # 1. Set capacity to base seats
    capacity = TOTAL_SEATS
    current_total_seats = capacity
    current_total_revenue = 0.0

    # 2. Sort groups (Greedy Knapsack: Highest profit first)
    # Python's list.sort() or sorted() uses the __lt__ method defined in Group
    groups.sort(key=lambda g: (-g.total_fare, g.members))

    allocated_groups = []
    waiting_groups = []

    # 3. Allocation Loop
    for group in groups:
        # Reset booking status for a fresh run
        group.is_booked = False
        
        if group.members <= current_total_seats:
            group.is_booked = True
            current_total_seats -= group.members
            current_total_revenue += group.total_fare
            allocated_groups.append(group)
        else:
            waiting_groups.append(group)

    return allocated_groups, waiting_groups, current_total_revenue, current_total_seats

def handle_cancellation(groups, cancel_id):
    """
    Handles a cancellation request and updates global state.
    Returns a message string and the group ID if successful, otherwise None.
    """
    global current_total_seats, current_total_revenue
    
    for group in groups:
        if group.id == cancel_id:
            if group.is_booked:
                fare = group.total_fare
                cancellation_fee = fare * CANCELLATION_FEE_PERCENTAGE
                refund_amount = fare - cancellation_fee

                # Update state
                group.is_booked = False
                current_total_seats += group.members
                current_total_revenue -= refund_amount
                
                message = (
                    f"Cancellation successful for Group {cancel_id} ({group.members} members).\n"
                    f"Fare: ${fare:.2f} | Fee Kept: ${cancellation_fee:.2f} | Refund Paid: ${refund_amount:.2f}\n"
                    f"Seats Freed: {group.members} | New Available Seats: {current_total_seats}\n"
                    f"New Total Revenue: ${current_total_revenue:.2f}"
                )
                return message, cancel_id

            else:
                return f"Group {cancel_id} is already unbooked or on the waiting list.", None
    
    return f"Error: Group ID {cancel_id} not found.", None