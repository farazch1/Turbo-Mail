from socket import *
import ssl
from base64 import b64encode
from flask import Flask,render_template,request

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

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
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



if __name__ == '__main__':
    app.run()
