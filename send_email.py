from socket import *
from base64 import *
import ssl
from envs import APP_PASSWORD

# add in prompt
userEmail = "2021ce36@student.uet.edu.pk"
userPassword = APP_PASSWORD
userDestinationEmail = "syednshah5@gmail.com"
userSubject = "Subject"
userBody = "Body"

msg = '{}.\r\n'.format(userBody)
endmsg = "\r\n.\r\n"
# Choose a mail server (e.g. Google mail server) and call it mailserver
mailserver = 'smtp.gmail.com'
mailPort = 587
# Create socket called clientSocket and establish a TCP connection with mailserver
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((mailserver, mailPort))
recv = clientSocket.recv(1024).decode()
print(recv)
if recv[:3] != '220':
    print('220 reply not received from server.')
# Send HELO command and print server response.
heloCommand = 'HELO Alice\r\n'
clientSocket.send(heloCommand.encode())
recv1 = clientSocket.recv(1024).decode()
print(recv1)
if recv1[:3] != '250':
    print('250 reply not received from server.')

# account authentication
strtlscmd = "STARTTLS\r\n".encode()
clientSocket.send(strtlscmd)
revc2 = clientSocket.recv(1024)

ssl_context = ssl.create_default_context()
sslClientSocket = ssl_context.wrap_socket(clientSocket, server_hostname= mailserver)


emailA = b64encode(userEmail.encode())
emailP = b64encode(userPassword.encode())

authorizationCMD = "AUTH LOGIN\r\n"

sslClientSocket.send(authorizationCMD.encode())
recv2 = sslClientSocket.recv(1024)
print(recv2)

sslClientSocket.send(emailA + "\r\n".encode())
recv3 = sslClientSocket.recv(1024)
print(recv3)

sslClientSocket.send(emailP + "\r\n".encode())
recv4 = sslClientSocket.recv(1024)
print(recv4)
# Send MAIL FROM command and print server response.
mailFrom = "Mail from: <{}>\r\n".format(userDestinationEmail)
sslClientSocket.send(mailFrom.encode())
recv5 = sslClientSocket.recv(1024)
print(recv5)
# Send RCPT TO command and print server response.
rcptto = "RCPT TO: <{}>\r\n".format(userDestinationEmail)
sslClientSocket.send(rcptto.encode())
recv6 = sslClientSocket.recv(1024)
print(recv6)
# Send DATA command and print server response.
data = 'DATA\r\n'
sslClientSocket.send(data.encode())
recv7 = sslClientSocket.recv(1024)
print(recv7)
# Send message data.
sslClientSocket.send("Subject: {}\n\n{}".format(userSubject, msg).encode())
# Message ends with a single period.
sslClientSocket.send(endmsg.encode())
recv8 = sslClientSocket.recv(1024)
print(recv8)
# Send QUIT command and get server response.
quitCMD = 'QUIT\r\n'
sslClientSocket.send(quitCMD.encode())
recv9 = sslClientSocket.recv(1024)
print(recv9)

sslClientSocket.close()
print('Success')

