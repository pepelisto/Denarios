import requests


def get_public_ip():
    try:
        # Use a service like 'httpbin' that echoes back your IP address
        response = requests.get('https://httpbin.org/ip')

        # Extract your public IP from the response
        ip_address = response.json().get('origin')

        return ip_address
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    public_ip = get_public_ip()
    print(f"Your public IP address is: {public_ip}")