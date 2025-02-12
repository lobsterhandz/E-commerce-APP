import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def display_menu():
    print("\n--- E-commerce Management System ---")
    print("1. Manage Customers")
    print("2. Manage Customer Accounts")
    print("3. Manage Products")
    print("4. Manage Orders")
    print("5. Exit")

def manage_customers():
    while True:
        print("\n--- Customer Management ---")
        print("1. Create Customer")
        print("2. Read Customer")
        print("3. Update Customer")
        print("4. Delete Customer")
        print("5. Back to Main Menu")

        choice = input("Enter your choice: ")
        if choice == "1":
            create_customer()
        elif choice == "2":
            read_customer()
        elif choice == "3":
            update_customer()
        elif choice == "4":
            delete_customer()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

def create_customer():
    name = input("Enter name: ")
    email = input("Enter email: ")
    phone_number = input("Enter phone number: ")
    data = {"name": name, "email": email, "phone_number": phone_number}

    response = requests.post(f"{BASE_URL}/customer", json=data)
    if response.status_code == 201:
        print("Customer created successfully!")
    else:
        print(f"Failed to create customer: {response.json().get('error')}")

def read_customer():
    customer_id = input("Enter customer ID: ")
    response = requests.get(f"{BASE_URL}/customer/{customer_id}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=4))
    else:
        print(f"Customer not found: {response.json().get('error')}")

def update_customer():
    customer_id = input("Enter customer ID to update: ")
    response = requests.get(f"{BASE_URL}/customer/{customer_id}")
    if response.status_code != 200:
        print(f"Customer not found: {response.json().get('error')}")
        return

    print("Leave field blank to keep current value.")
    current_data = response.json()
    name = input(f"Enter new name ({current_data['name']}): ") or current_data['name']
    email = input(f"Enter new email ({current_data['email']}): ") or current_data['email']
    phone_number = input(f"Enter new phone number ({current_data['phone_number']}): ") or current_data['phone_number']

    data = {"name": name, "email": email, "phone_number": phone_number}
    response = requests.put(f"{BASE_URL}/customer/{customer_id}", json=data)
    if response.status_code == 200:
        print("Customer updated successfully!")
    else:
        print(f"Failed to update customer: {response.json().get('error')}")

def delete_customer():
    customer_id = input("Enter customer ID to delete: ")
    response = requests.delete(f"{BASE_URL}/customer/{customer_id}")
    if response.status_code == 200:
        print("Customer deleted successfully!")
    else:
        print(f"Failed to delete customer: {response.json().get('error')}")

# Similarly, create functions for managing Customer Accounts, Products, and Orders.

def main():
    while True:
        display_menu()
        choice = input("Enter your choice: ")
        if choice == "1":
            manage_customers()
        elif choice == "2":
            # manage_customer_accounts() - similar to `manage_customers()`
            pass
        elif choice == "3":
            # manage_products() - similar structure to `manage_customers()`
            pass
        elif choice == "4":
            # manage_orders() - similar structure to `manage_customers()`
            pass
        elif choice == "5":
            print("Exiting system. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
