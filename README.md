# Cowin-Auto-Scheduler

Cowin Auto Scheduler takes your City or PIN code as an input and automatically notifies you via email when any booking is available.


# Script Path


```mermaid
graph
A((Start)) --> B(Enter Email for Getting Notification)
B --> C(Enter Phone Number For Getting OTP)
C --> D{Select}
D -- Search By City --> E(Enter State Code)
E --> F(Enter City Code)
F --> G(Enter Preffered Pincodes)

D -- Search By PIN --> H(Enter Pincode)

G --> I((Wait until Found))
H --> I
I -- Found Centers --> J(Select Center by its Index To Book Appointment)
J --> K(Enter OTP that came on your phone)
K --> L(Select the Person by Index)
L --> M(Enter Captcha)
M --> N((Ching Chong MF. Your Appointment is Scheduled))
```