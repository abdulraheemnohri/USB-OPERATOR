package com.usboperator.companion
import android.app.Activity
import android.hardware.usb.UsbManager
import android.os.Bundle
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
class MainActivity : Activity() {
 private lateinit var output: TextView
 override fun onCreate(savedInstanceState: Bundle?) { super.onCreate(savedInstanceState); output=TextView(this).apply { textSize=15f; setPadding(20,20,20,20) }; val scan=Button(this).apply { text="Scan USB OTG devices"; setOnClickListener { scanDevices() } }; val layout=LinearLayout(this).apply { orientation=LinearLayout.VERTICAL; addView(scan); addView(ScrollView(this@MainActivity).apply { addView(output) }) }; setContentView(layout); scanDevices() }
 private fun scanDevices() { val manager=getSystemService(USB_SERVICE) as UsbManager; val devices=manager.deviceList.values; output.text=if(devices.isEmpty()) "No USB devices detected. Connect a supported OTG device." else devices.joinToString("\\n\\n") { d -> String.format("%s\\nVID: %04X PID: %04X\\nInterfaces: %d",d.deviceName,d.vendorId,d.productId,d.interfaceCount) }; output.append("\\n\\nRead-only enumeration only. USB permission and a reviewed protocol adapter are required before communication.") }
}
