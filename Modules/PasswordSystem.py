import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def save_credentials(data, file_path):
    # Save the data to the JSON file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def add_credentials(camera_label):
    # Get user input for credentials
    username = input("Enter username: ")
    password = input("Enter password: ")
    ip_address = input("Enter IP address: ")

    return {
        'camera_label': camera_label,
        'username': username,
        'password': password,
        'ip_address': ip_address
    }

def edit_credentials(credentials):
    print("Current credentials:")
    for key, value in credentials.items():
        print(f"{key}: {value}")

    # Get user input for editing
    new_username = input("Enter new username (press Enter to keep existing): ")
    new_password = input("Enter new password (press Enter to keep existing): ")
    new_ip_address = input("Enter new IP address (press Enter to keep existing): ")

    # Update credentials with new values
    credentials['username'] = new_username if new_username else credentials['username']
    credentials['password'] = new_password if new_password else credentials['password']
    credentials['ip_address'] = new_ip_address if new_ip_address else credentials['ip_address']

def get_credentials_for_camera(data, camera_label):
    for camera in data.get('Cameras', []):
        if camera['camera_label'] == camera_label:
            return {
                'username': camera['username'],
                'password': camera['password'],
                'ip_address': camera['ip_address']
            }
    return None

def print_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            print(data['Cameras'][0])
        return data
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading JSON file at '{file_path}': {e}")
        return {}

def read_json_file():  
    root = Tk()
    root.withdraw()

    try:
        file_path = askopenfilename(title="Select Credentials File", filetypes=[("JSON files", "*.json")])
        
        if file_path:
            with open(file_path, 'r') as file:
                data = json.load(file)
                return data, file_path
        else:
            print("No file selected.")
            return {}, file_path

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading credentials file: {e}")
        return {}, file_path
   
    finally:
        root.destroy()  # Close the Tkinter window

def password_save_process(data, file_path):
    # Load existing data from the file
    data = data
    file_path = file_path
    
    if data == {} and file_path == "":
        data, file_path = read_json_file()
    
    # print(data, file_path)
    # print(str(file_path))

    show_or_add = input("Add, Show, Edit, Quit, or Get Credentials: ")
    
    if show_or_add.lower() == "quit":
        return {}
    
    if show_or_add.lower() == "add":
        # Create Cameras array if it doesn't exist
        if 'Cameras' not in data:
            data['Cameras'] = []

        # Allow the user to add multiple sets of credentials
        while True:
            camera_label = f"camera_{len(data['Cameras']) + 1}"
            credentials = add_credentials(camera_label)

            # Add new credentials to the Cameras array
            data['Cameras'].append(credentials)

            # Ask the user if they want to add more credentials
            more_credentials = input("Do you want to add more credentials? (yes/no): ").lower()
            save_credentials(data, file_path)
            if more_credentials != 'yes':
                password_save_process(data, file_path) # Restart until Quit 
                
    elif show_or_add.lower() == "show":
        # Display the list of all cameras
        print("List of all cameras:", data.get('Cameras', []))
        
        password_save_process(data, file_path) # Restart until Quit 
        
    elif show_or_add.lower() == "edit":
        # Allow the user to edit credentials for a specific camera
        camera_to_edit = input("Enter the camera label to edit: ")
        for camera in data.get('Cameras', []):
            if camera['camera_label'] == camera_to_edit:
                edit_credentials(camera)
                save_credentials(data, file_path)
                print("Credentials updated successfully.")
                
                password_save_process(data, file_path) # Restart until Quit
        else:
            print(f"Camera with label '{camera_to_edit}' not found.")
                
            password_save_process() # Restart until Quit    
                           
    elif show_or_add.lower() == "get credentials":
        # Get credentials for a specific camera
        camera_to_get = input("Enter the camera label to get credentials: ")
        credentials = get_credentials_for_camera(data, camera_to_get)
        if credentials:
            print(f"Credentials for {camera_to_get}:")
            print(f"Username: {credentials['username']}")
            print(f"Password: {credentials['password']}")
            print(f"IP Address: {credentials['ip_address']}")
            
            password_save_process(data, file_path) # Restart until Quit            
        else:
            print(f"Camera with label '{camera_to_get}' not found.")
    
            password_save_process(data, file_path) # Restart until Quit 