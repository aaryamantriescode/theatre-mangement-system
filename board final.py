import mysql.connector

obj = mysql.connector.connect(host="localhost", user="root", password='admin@123')
mycursor = obj.cursor()
# Create the sys database if it doesn't exist
mycursor.execute("CREATE DATABASE IF NOT EXISTS new4")
mycursor.execute("USE new4")

# Create tables0

def create_table():
 mycursor.execute("""
     CREATE TABLE IF NOT EXISTS movies2 (
         id INT AUTO_INCREMENT PRIMARY KEY,
         title VARCHAR(255) NOT NULL UNIQUE,
         duration INT NOT NULL,
         protagonist VARCHAR(40)
     ) AUTO_INCREMENT = 1
   """)
 mycursor.execute("""
     CREATE TABLE IF NOT EXISTS seats1 (
         id INT AUTO_INCREMENT PRIMARY KEY,
         seat_number INT NOT NULL,
         is_reserved BOOLEAN DEFAULT 0,
         price DECIMAL(10, 2) DEFAULT 0.0,         
         UNIQUE (seat_number)
     )
 """)
 obj.commit()

 mycursor.execute("""
     CREATE TABLE IF NOT EXISTS screening2 (
         id INT AUTO_INCREMENT PRIMARY KEY,
         time VARCHAR(255) NOT NULL,
         screen_number INT NOT NULL,
         UNIQUE (time, screen_number)
     )
 """)
 obj.commit()

 mycursor.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        seat_number INT NOT NULL,
        customer_name VARCHAR(255) NOT NULL,
        reservation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
     )
 """)
 obj.commit()

# Create the booking table separately
 mycursor.execute("""
    CREATE TABLE IF NOT EXISTS booking2 (
        id INT AUTO_INCREMENT PRIMARY KEY,
        movie_id INT,
        seats_id INT,
        reservation_id INT,
        tickets INT,
        FOREIGN KEY (movie_id) REFERENCES movies2(id),
        FOREIGN KEY (seats_id) REFERENCES seats1(id),
        FOREIGN KEY (reservation_id) REFERENCES reservations(id))
 """)
 obj.commit()

create_table()

for seat_number in range(1, 51):
    # Check if the seat number already exists in the table
    mycursor.execute("SELECT seat_number FROM seats1 WHERE seat_number = %s", (seat_number,))
    existing_seat = mycursor.fetchone()

    # If the seat number doesn't exist, insert it
    if not existing_seat:
        mycursor.execute("INSERT INTO seats1 (seat_number) VALUES (%s)", (seat_number,))
# Commit the changes
obj.commit()


# Insert data into the 'movies' table

query = "INSERT IGNORE INTO movies2 (title, duration, protagonist) VALUES (%s, %s, %s)"
data_movies = [
    ('RaOne', 155, 'ShahRukhKhan'),
    ('Dream Girl', 160, 'AayushManKhuranna'),
    ('DeadPool', 140, 'Ryan Reynolds'),
    ('Agent Vinod', 159, 'SaifAliKhan'),
    ('Baby', 170, 'AkkshayKumar')
]
mycursor.executemany(query, data_movies)

# Commit the changes
obj.commit()


#adding seats
def set_seat_prices():
    price_brackets = [(1, 10, 100), (11, 20, 200), (21, 30, 300), (31, 40, 400), (41, 50, 500)]
    for start, end, price in price_brackets:
        mycursor.execute("""
            UPDATE seats1
            SET price = %s
            WHERE seat_number BETWEEN %s AND %s
        """, (price, start, end))
    obj.commit()
set_seat_prices()

def display_available_seats():
    price_brackets = [(1, 10), (11, 20), (21, 30), (31, 40), (41, 50)]
    for start, end in price_brackets:
        mycursor.execute("""
            SELECT seat_number, price
            FROM seats1
            WHERE is_reserved = 0 AND seat_number BETWEEN %s AND %s
        """, (start, end))
        available_seats = mycursor.fetchall()
        if available_seats:
            print("Available seats (Price: {}):".format(available_seats[0][1]), [seat[0] for seat in available_seats])





def reserve_and_book_seat(seat_number, customer_name, movie_title):
    # Check if the seat exists in the seats table
    mycursor.execute("SELECT is_reserved FROM seats1 WHERE seat_number = %s", (seat_number,))
    seat_data = mycursor.fetchone()

    if seat_data is None:
        print(f"Seat {seat_number} does not exist.")
        return

    if seat_data[0] == 1:
        print(f"Seat {seat_number} is already reserved.")
        return

    # Check if the movie exists
    mycursor.execute("SELECT id FROM movies2 WHERE title = %s", (movie_title,))
    movie_id = mycursor.fetchone()

    if movie_id is None:
        print(f"Movie '{movie_title}' does not exist.")
        return

    # Insert reservation into reservations table
    mycursor.execute("""
        INSERT INTO reservations (seat_number, customer_name)
        VALUES (%s, %s)
    """, (seat_number, customer_name))

    # Get the latest reservation ID
    reservation_id = mycursor.lastrowid

    # Mark the seat as reserved in the seats table
    mycursor.execute("UPDATE seats1 SET is_reserved = 1 WHERE seat_number = %s", (seat_number,))

    # Insert into booking table
    mycursor.execute("INSERT INTO booking2 (movie_id, reservation_id) VALUES (%s, %s)", (movie_id[0], reservation_id))

    obj.commit()
    print(f"Seat {seat_number} reserved and booked for '{movie_title}' successfully!")

    mycursor.execute("""
        SELECT r.seat_number, r.reservation_date, m.title, m.duration, s.price
        FROM reservations r
        JOIN booking2 b ON r.id = b.reservation_id
        JOIN movies2 m ON b.movie_id = m.id
        JOIN seats1 s ON r.seat_number = s.seat_number
        WHERE r.id = %s
    """, (reservation_id,))
    receipt = mycursor.fetchone()

    if receipt:
        print("\nThank you for booking with us!")
        print("Seat Number | Reservation Date      | Title | Duration (minutes) | Price")
        print("{:11} | {} | {} | {:17} | {}".format(
            receipt[0], receipt[1], receipt[2], receipt[3], receipt[4]))




    # View reservations
def view_reservations(customer_name):
        mycursor.execute("""
            SELECT id,seat_number, reservation_date
            FROM reservations
            WHERE customer_name = %s
        """, (customer_name,))
        reservations = mycursor.fetchall()
        if not reservations:
            print(f"No reservations found for {customer_name}.")
        else:
            print(f"Reservations for {customer_name}:")
            for id,seat, reservation_date in reservations:
                print(f"id is  {id} Seat {seat} was reserved on {reservation_date}")


    # Cancel reservations

def add_movie(title, duration, protagonist):
    mycursor.execute("INSERT INTO movies2 (title,duration, protagonist ) VALUES (%s, %s, %s)", (title, duration, protagonist))
    obj.commit()

# Function to list theaters
def list_movie():
    mycursor.execute("SELECT * FROM movies2")
    theaters = mycursor.fetchall()
    for theater in theaters:
        print("ID: {}, title: {}, duration: {}, protagonist: {}".format(theater[0], theater[1], theater[2], theater[3]))



def list_bookings():
    try:
        mycursor.execute("""
        SELECT r.seat_number, r.reservation_date, m.title, m.duration, s.price
        FROM booking2 b
        INNER JOIN reservations r ON b.reservation_id = r.id
        INNER JOIN movies2 m ON b.movie_id = m.id
        INNER JOIN seats1 s ON r.seat_number = s.seat_number
        """)
        bookings = mycursor.fetchall()
        if not bookings:
            print("No bookings found.")
        else:
            print("Seat Number | Reservation Date | Title | Duration (minutes) | Price")
            for booking in bookings:
                print("{:11} | {} | {} | {} | {}".format(
                    booking[0], booking[1], booking[2], booking[3], booking[4]))
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def delete_movie(title):
    # Check if the movie with the provided title exists
    mycursor.execute("SELECT id FROM movies2 WHERE title = %s", (title,))
    movie_id = mycursor.fetchone()

    if movie_id:
        # Delete the movie from the movies2 table
        mycursor.execute("DELETE FROM movies2 WHERE id = %s", (movie_id[0],))
        obj.commit()
        print(f"Movie with title '{title}' deleted successfully!")
    else:
        print(f"Movie with title '{title}' not found.")

def cancel_ticket(customer_name, title):
    # First, retrieve the reservation id and seat number based on the customer name
    mycursor.execute("""
        SELECT r.id, r.seat_number
        FROM reservations r
        WHERE r.customer_name = %s
    """, (customer_name,))
    reservation_data = mycursor.fetchone()

    if not reservation_data:
        print(f"No reservations found for {customer_name}.")
        return

    reservation_id, seat_number = reservation_data

    # Next, retrieve the movie id based on the provided title
    mycursor.execute("SELECT id FROM movies2 WHERE title = %s", (title,))
    movie_id = mycursor.fetchone()

    if not movie_id:
        print(f"Movie with title '{title}' not found.")
        return

    # Now, check if there's a booking for the given reservation id and movie id
    mycursor.execute("""
        SELECT 1
        FROM booking2
        WHERE movie_id = %s AND reservation_id = %s
    """, (movie_id[0], reservation_id))
    exists = mycursor.fetchone()

    if not exists:
        print(f"No matching booking found for {customer_name} and movie '{title}'.")
        return

    # Delete the booking from the booking2 table
    mycursor.execute("""
        DELETE FROM booking2
        WHERE movie_id = %s AND reservation_id = %s
    """, (movie_id[0], reservation_id))

    # Also delete the reservation from the reservations table
    mycursor.execute("""
        DELETE FROM reservations
        WHERE id = %s
    """, (reservation_id,))

    # Set the seat as available in the seats1 table
    mycursor.execute("""
        UPDATE seats1
        SET is_reserved = 0
        WHERE seat_number = %s
    """, (seat_number,))

    obj.commit()
    print(f"Booking for movie '{title}' canceled successfully!")



if __name__ == "__main__":
    create_table()

    while True:
        print("\nOptions:")
        print("1. Add movies")
        print("2. List movies")
        print("3. Delete Movie")
        print("4. show available seats ")
        print("5. reserve seats ")
        print("6. show reservation ")
        print("7. List Bookings")
        print("8. Cancel Ticket")
        print("0. Quit")

        choice = input("Enter your choice: ")

        if choice == '1':
            title = input("Enter movie name: ")
            duration = int(input("Enter movie duration: "))
            protagonist = input("Enter protagonist name")
            add_movie(title, duration, protagonist)
            print("movie added successfully!")

        elif choice == '2':
            print("\nList of Movies:")
            list_movie()
        elif choice == '3':
            title = input("Enter the title of the movie you want to delete: ")
            delete_movie(title)
        elif choice == '4':
            display_available_seats()
            print("These are the available seats")
        elif choice == '5':
            seat_number = input("Enter seat no: ")
            customer_name = input("Enter customer name: ")
            movie_title = input("Enter movie title: ")
            reserve_and_book_seat(seat_number, customer_name, movie_title)

        elif choice =='6':
            name=input("enter your name ")
            view_reservations(name)



        elif choice == '7':
            list_bookings()


        elif choice == '8':
            name = input("Enter your name: ")
            title = input("Enter the title of the movie you want to cancel: ")
            cancel_ticket(name, title)
        elif choice == '0':
            break


        else:
            print("Invalid choice. Please try again.")

    obj.close()






























