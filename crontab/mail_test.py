import smtplib
 
to = 'carlos.biomundo@gmail.com'
user = 'informes@biomundo.eu'
pwd = '0rganic022.'
#smtpserver = smtplib.SMTP("smtp.gmail.com",587)
smtpserver = smtplib.SMTP("mail.biomundo.eu",587)
smtpserver.ehlo()
smtpserver.starttls()
smtpserver.ehlo
smtpserver.login(user, pwd)
header = 'To:' + to + '\n' + 'From: ' + user + '\n' + 'Subject:Prueba de correo \n'
print header
msg = header + '\n Prueba de envio de informes@biomundo.eu \n\n'
smtpserver.sendmail(user, to, msg)
print 'done!'
smtpserver.close()
