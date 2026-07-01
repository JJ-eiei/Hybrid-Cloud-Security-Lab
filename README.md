### Hybrid Cloud SIEM - Wazuh + MQTT + Discord

	
โปรเจคนี้ทำขึ้นมาเพื่อศึกษาการทำงานสาย Blue Team / SOC โดยมี concept หลักๆ คือการจำลองระบบรักษาความปลอดภัยแบบ Hybrid Cloud โดยตั้ง SIEM ไว้ที่คอมบ้าน แล้วเชื่อมไป monitor เซิร์ฟเวอร์เป้าหมายที่รันอยู่บน Google Cloud โดยเป้าหมายคือถ้ามีแฮกเกอร์พยายามจะเจาะระบบ ไม่ว่าจะเป็นทาง SSH หรือพยายามเจาะเข้า IoT Broker (MQTT) ระบบต้องตรวจจับได้ และส่งแจ้งเตือนเข้า Discord ของเราแบบ Real-time

## Tech Stack

- **pfSense - (Firewall/Router) ประจำ Home Lab ทำหน้าที่จัดการ Routing และคัดกรอง traffic ทั้งหมดก่อนเข้ามาถึงวง network ในบ้าน
    
- **Wazuh (SIEM): - ตั้งอยู่ที่เครื่อง On-premise อยู่หลัง pfSense ทำหน้าที่เป็นตัว monitor log
    
- **Google Cloud Platform (GCP):** จำลองเป็นเป้าหมาย รัน Ubuntu + Mosquitto (MQTT Broker)
    
- **Tailscale: - ทำ VPN Tunnel เชื่อมเครื่องบ้านกับ cloud ให้คุยกันได้
    
- **Python 3 & Discord Webhook - เขียนสคริปต์ดึง Log ยิงแจ้งเตือนเข้า Discord
    

## ฟีเจอร์หลัก

1. **Detect SSH Brute-force - ตรวจจับคนเดารหัสผ่านเข้าเครื่องเป้าหมาย
    
2. **Detect MQTT Brute-force: - เขียน Custom Decoder ดักจับคนพยายามเจาะเข้า Mosquitto Broker
    
3. **Real-time Alert:** ตั้ง Rule Level 12 (Critical) โดยให้แจ้งเตือนเข้า Discord ทันที
    

## โครงสร้างการทำงาน (Architecture)

1. **Home Lab Network:** มี **pfSense** เป็น Firewall คุมประตูทางเข้า-ออกของเน็ตเวิร์กบ้าน คอยป้องกันเครื่อง Wazuh Manager ที่อยู่ข้างใน
    
2. ติดตั้ง **Wazuh Agent** ไว้ที่เครื่องเป้าหมายบน GCP
    
3. เมื่อมีการพยายามล็อกอินผิดพลาด เช่น รัน `mosquitto_sub` แล้วใส่รหัสผิด Agent จะดูด Log ส่งผ่าน **Tailscale** ข้ามอินเทอร์เน็ต มุดผ่าน pfSense กลับมาที่เครื่อง Wazuh ในบ้าน
    
4. **Wazuh Manager** จะเอา Log มาเทียบกับ `local_rules.xml` และ `local_decoder.xml` ที่เขียนดักไว้
    
5. ถ้าตรงกับเงื่อนไข (Rule 100020) ตัว `wazuh-integratord` จะไปเรียกสคริปต์ Python (`custom-discord`)
    
6. สคริปต์ Python จะแปลงข้อมูลเป็น JSON แล้วยิง POST Request วิ่งออกเน็ตไปแจ้งเตือนที่ช่อง Discord
    

## Troubleshooting



- **Wazuh ส่งเข้า Discord ไม่ได้ (Exit status 7)**
    
    - **ปัญหา - ตอนแรกใช้ integration ชื่อ `slack` ใน `ossec.conf` แล้วเปลี่ยน URL เป็น Discord แต่มันพัง
        
    - **วิธีแก้ -  Discord ไม่รองรับ Format ของ Slack เลยต้องเขียน Python สคริปต์ขึ้นมาเอง (`custom-discord`) แล้วใช้ request ยิงเข้า Discord แบบตรงๆ
        
- **Wazuh start ไม่ได้หลังเพิ่ม rule**
    
    - **ปัญหา - พอเพิ่ม Rule จับ MQTT ไปแล้ว restart พังเลย เช็ค log เจอว่า `Invalid decoder name: 'syslog'`
        
    - **วิธีแก้ - Log ของ Mosquitto มันเป็นแค่ตัวเลข Timestamp ไม่ใช่ Syslog ปกติ เลยต้องไปสร้าง Custom Decoder ให้มันดักคำว่า `not authorised`
        
- **Discord ไม่แจ้งเตือนและ DNS ไม่ทำงาน**
    
    - **ปัญหา - Alert เด้งในหน้า Dashboard แล้ว แต่ใน Discord ไม่แจ้งเตือน จึงเช็ค log เจอ `Name or service not known`
        
    - **วิธีแก้ - เครื่องตื่นจากโหมด Sleep แล้ว Network/DNS รวน ทำให้ Wazuh ที่อยู่ใน Chroot Jail ออกเน็ตไปหาเว็บไม่ได้ ต้องใส่ DNS เข้าไปตรงๆด้วยคำสั่ง  `echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf` แล้ว restart wazuh Manager ถึงจะหาย
