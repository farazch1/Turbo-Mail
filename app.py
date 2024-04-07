from socket import *
import ssl
from base64 import b64encode
from flask import Flask, render_template, request, jsonify
import email
import re

# radix healthcare app password
APP_PASSWORD = "etjx qvrf pwnp xhrk"

class EmailClient:
    
    def __init__(self, email, password, destination_email, subject, body):
        self.email = email
        self.password = password
        self.destination_email = destination_email
        self.subject = subject
        self.body = body
        self.msg = '{}.\r\n'.format(body)
        self.endmsg = "\r\n.\r\n"
        self.mailserver = 'smtp.gmail.com'
        self.mail_port = 587
        self.client_socket = socket(AF_INET, SOCK_STREAM)

    def connect_to_server(self):
        self.client_socket.connect((self.mailserver, self.mail_port))
        recv = self.client_socket.recv(1024).decode()
        print(recv)
        if recv[:3] != '220':
            print('220 reply not received from server.')

    def send_helo_command(self):
        helo_command = 'HELO Alice\r\n'
        self.client_socket.send(helo_command.encode())
        recv1 = self.client_socket.recv(1024).decode()
        print(recv1)
        if recv1[:3] != '250':
            print('250 reply not received from server.')

    def start_tls(self):
        strtlscmd = "STARTTLS\r\n".encode()
        self.client_socket.send(strtlscmd)
        recv2 = self.client_socket.recv(1024)

        ssl_context = ssl.create_default_context()
        self.ssl_client_socket = ssl_context.wrap_socket(self.client_socket, server_hostname=self.mailserver)

    def authenticate(self):
        email_encoded = b64encode(self.email.encode())
        password_encoded = b64encode(self.password.encode())

        authorization_cmd = "AUTH LOGIN\r\n"
        self.ssl_client_socket.send(authorization_cmd.encode())
        recv2 = self.ssl_client_socket.recv(1024)
        print(recv2)

        self.ssl_client_socket.send(email_encoded + "\r\n".encode())
        recv3 = self.ssl_client_socket.recv(1024)
        print(recv3)

        self.ssl_client_socket.send(password_encoded + "\r\n".encode())
        recv4 = self.ssl_client_socket.recv(1024)
        print(recv4)

    def send_email(self):
        mail_from = "Mail from: <{}>\r\n".format(self.destination_email)
        self.ssl_client_socket.send(mail_from.encode())
        recv5 = self.ssl_client_socket.recv(1024)
        print(recv5)

        rcpt_to = "RCPT TO: <{}>\r\n".format(self.destination_email)
        self.ssl_client_socket.send(rcpt_to.encode())
        recv6 = self.ssl_client_socket.recv(1024)
        print(recv6)

        data = 'DATA\r\n'
        self.ssl_client_socket.send(data.encode())
        recv7 = self.ssl_client_socket.recv(1024)
        print(recv7)

        self.ssl_client_socket.send("Subject: {}\n\n{}".format(self.subject, self.msg).encode())
        self.ssl_client_socket.send(self.endmsg.encode())
        recv8 = self.ssl_client_socket.recv(1024)
        print(recv8)

    def quit(self):
        quit_cmd = 'QUIT\r\n'
        self.ssl_client_socket.send(quit_cmd.encode())
        recv9 = self.ssl_client_socket.recv(1024)
        print(recv9)

    def close_connection(self):
        self.ssl_client_socket.close()
        print('Success')

    def run_all(self):

        self.connect_to_server()
        self.send_helo_command()
        self.start_tls()
        self.authenticate()
        self.send_email()
        self.quit()
        self.close_connection()

class InboxClient:
    def __init__(self, server, port, email, password):
        self.server = server
        self.port = port
        self.email = email
        self.password = password
        self.context = ssl.create_default_context()

    def connect(self):
        self.sock = socket.create_connection((self.server, self.port))
        self.ssock = self.context.wrap_socket(self.sock, server_hostname=self.server)
        self.receive_greeting()

    def receive_greeting(self):
        greeting = self.ssock.recv(1024)

    def login(self):
        self.send_command(f'LOGIN {self.email} {self.password}\r\n')
        self.response = self.ssock.recv(1024)

    def select_mailbox(self, mailbox='INBOX'):
        self.send_command(f'SELECT {mailbox}\r\n')
        self.response = self.ssock.recv(1024)

    def get_total_messages(self, mailbox='INBOX'):
        self.send_command(f'STATUS {mailbox} (MESSAGES)\r\n')
        response = self.ssock.recv(1024).decode()
        num_messages = int(re.search(r"MESSAGES\s+(\d+)", response).group(1))
        return num_messages

    def fetch_message(self, message_number):
        self.send_command(f'FETCH {message_number} RFC822\r\n')
        self.response = self.ssock.recv(8192)

    def parse_message(self):
        msg = email.message_from_bytes(self.response)
        subject = msg["Subject"] if msg["Subject"] else "No subject"
        sender = msg["From"] if msg["From"] else "No sender"
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    body += part.get_payload(decode=True).decode()
        else:
            body = msg.get_payload(decode=True).decode()
        return subject, sender, body

    def send_command(self, command):
        self.ssock.sendall(command.encode())

    def logout(self):
        self.send_command(b'LOGOUT\r\n')
        self.ssock.close()
        print("LOGGED OUT")


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def hello_world():  # put application's code here
    if request.method == 'POST':
        to_mail = request.form['to']
        from_mail = request.form['from']
        subject = request.form['subject']
        message = request.form['message']
        print(to_mail, from_mail, subject, message)

        runner = EmailClient(from_mail,APP_PASSWORD,to_mail,subject,message)
        runner.run_all()
        
        return render_template("home.html", show_tick=True)
    else:
        return render_template("home.html")


@app.route('/inbox')
def display_mail():  # put application's code here
    # # IMAP server settings for Gmail
    # IMAP_SERVER = 'imap.gmail.com'
    # IMAP_PORT = 993
    # EMAIL = 'healthcere.radix@gmail.com'
    # PASSWORD = APP_PASSWORD
    # client = EmailClient(IMAP_SERVER, IMAP_PORT, EMAIL, PASSWORD)
    # # Establish connection
    # client.connect()
    #
    # # Login to account
    # client.login()
    #
    # # Select mailbox
    # client.select_mailbox()
    #
    # # Get total number of messages
    # num_messages = client.get_total_messages()
    #
    # # Fetch the most recent message
    # client.fetch_message(num_messages)
    #
    # # Parse the email
    # subject, sender, body = client.parse_message()
    #
    # # Print the results
    # print("Subject:", subject)
    # print("From:", sender)
    # print("Body:", body)
    #
    # mail = []
    # for i in range(1, num_messages + 1):
    #     client.fetch_message(i)
    #     subject, sender, body = client.parse_message()
    #     mail.append({"Subject": subject, "From": sender, "Body": body})
    mail = [
            {'subject': 'Welcome to our service', 'sender': 'info@example.com', 'id': 1},
            {'subject': 'Your order confirmation', 'sender': 'sales@shop.com', 'id': 2}
        ]
    return render_template("inbox.html",mail_inbox_items = mail)



@app.route('/mail/<int:message_id>')
def get_message(message_id):
    # # IMAP server settings for Gmail
    # IMAP_SERVER = 'imap.gmail.com'
    # IMAP_PORT = 993
    # EMAIL = 'healthcere.radix@gmail.com'
    # PASSWORD = APP_PASSWORD
    # client_spec = EmailClient(IMAP_SERVER, IMAP_PORT, EMAIL, PASSWORD)
    # client_spec.connect()
    # client_spec.login()
    # client_spec.select_mailbox()
    # num_messages = client_spec.get_total_messages()
    # client_spec.fetch_message(num_messages)
    # subject, sender, body = client_spec.parse_message()
    #
    # # Print the results
    # print("Subject:", subject)
    # print("From:", sender)
    # print("Body:", body)
    #
    # particular_mail = []
    # def get_message_details(message_id):
    #     client_spec.fetch_message(message_id)
    #     subject, sender, body = client_spec.parse_message()
    #     particular_mail.append({"ID": message_id, "Subject": subject, "From": sender, "Body": body})
    #
    #
    # extra_var = get_message_details(message_id)
    particular_mail = [
        {'subject': 'Welcome to our service', 'sender': 'info@example.com', 'id': 1, 'content': 'this is first message'},
        {'subject': 'Your order confirmation', 'sender': 'sales@shop.com', 'id': 2, 'content': 'this is second message'}
    ]
    message = particular_mail[message_id-1]
    print(jsonify(message))
    return jsonify(message)



if __name__ == '__main__':
    app.run()
