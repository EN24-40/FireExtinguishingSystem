#include <QApplication>
#include <QThread>
#include <QMutex>
#include <QMessageBox>

#include <QColor>
#include <QLabel>
#include <QtDebug>
#include <QString>
#include <QPushButton>
#include <QImageWriter>  // Added for QImageWriter

#include "LeptonThread.h"
#include "MyLabel.h"
#include <cstdlib>

//for web application
// #include <QNetworkAccessManager>
// #include <QNetworkRequest>
// #include <QNetworkReply>
// #include <QBuffer>
// #include <QDebug>
//#include <QWebView>

void printUsage(char *cmd) {
        char *cmdname = basename(cmd);
	printf("Usage: %s [OPTION]...\n"
               " -h      display this help and exit\n"
               " -cm x   select colormap\n"
               "           1 : rainbow\n"
               "           2 : grayscale\n"
               "           3 : ironblack [default]\n"
               " -tl x   select type of Lepton\n"
               "           2 : Lepton 2.x [default]\n"
               "           3 : Lepton 3.x\n"
               "               [for your reference] Please use nice command\n"
               "                 e.g. sudo nice -n 0 ./%s -tl 3\n"
               " -ss x   SPI bus speed [MHz] (10 - 30)\n"
               "           20 : 20MHz [default]\n"
               " -min x  override minimum value for scaling (0 - 65535)\n"
               "           [default] automatic scaling range adjustment\n"
               "           e.g. -min 30000\n"
               " -max x  override maximum value for scaling (0 - 65535)\n"
               "           [default] automatic scaling range adjustment\n"
               "           e.g. -max 32000\n"
               " -d x    log level (0-255)\n"
               "", cmdname, cmdname);
	return;
}
// funtion for web application
// void sendImageToServer(const QImage &image)
// {
//    QNetworkAccessManager manager;
//     QUrl url("http://10.0.0.151/var/www/html/upload.php");  // Update with your server URL
//     QNetworkRequest request(url);

//     // Convert QImage to byte array
//     QByteArray imageData;
//     QBuffer buffer(&imageData);
//     buffer.open(QIODevice::WriteOnly);
//     image.save(&buffer, "PNG");  // Save QImage as PNG to byte array

//     // Set content type and POST image data to server
//     request.setHeader(QNetworkRequest::ContentTypeHeader, "image/png");  // Set correct content type
//     QNetworkReply *reply = manager.post(request, imageData);

//     // Handle server response
//     QObject::connect(reply, &QNetworkReply::finished, [=]() {
//         if (reply->error() == QNetworkReply::NoError) {
//             qDebug() << "Image uploaded successfully!";
//             qDebug() << "Server response:" << reply->readAll();  // Optionally read server response
//         } else {
//             qDebug() << "Error uploading image:" << reply->errorString();
//         }
//         reply->deleteLater();
//     });
// }

int main( int argc, char **argv )
{
	int typeColormap = 4; // colormap_ironblack
	int typeLepton = 2; // Lepton 2.x
	int spiSpeed = 20; // SPI bus speed 20MHz
	int rangeMin = -1; //
	int rangeMax = -1; //
	int loglevel = 0;
	for(int i=1; i < argc; i++) {
		if (strcmp(argv[i], "-h") == 0) {
			printUsage(argv[0]);
			exit(0);
		}
		else if (strcmp(argv[i], "-d") == 0) {
			int val = 3;
			if ((i + 1 != argc) && (strncmp(argv[i + 1], "-", 1) != 0)) {
				val = std::atoi(argv[i + 1]);
				i++;
			}
			if (0 <= val) {
				loglevel = val & 0xFF;
			}
		}
		else if ((strcmp(argv[i], "-cm") == 0) && (i + 1 != argc)) {
			int val = std::atoi(argv[i + 1]);
			if ((val == 1) || (val == 2) || (val == 3)) {
				typeColormap = val;
				i++;
			}
		}
		else if ((strcmp(argv[i], "-tl") == 0) && (i + 1 != argc)) {
			int val = std::atoi(argv[i + 1]);
			if (val == 3) {
				typeLepton = val;
				i++;
			}
		}
		else if ((strcmp(argv[i], "-ss") == 0) && (i + 1 != argc)) {
			int val = std::atoi(argv[i + 1]);
			if ((10 <= val) && (val <= 30)) {
				spiSpeed = val;
				i++;
			}
		}
		else if ((strcmp(argv[i], "-min") == 0) && (i + 1 != argc)) {
			int val = std::atoi(argv[i + 1]);
			if ((0 <= val) && (val <= 65535)) {
				rangeMin = val;
				i++;
			}
		}
		else if ((strcmp(argv[i], "-max") == 0) && (i + 1 != argc)) {
			int val = std::atoi(argv[i + 1]);
			if ((0 <= val) && (val <= 65535)) {
				rangeMax = val;
				i++;
			}
		}
	}

	//create the app
	QApplication a( argc, argv );
	
	QWidget *myWidget = new QWidget;
	myWidget->setGeometry(400, 300, 340, 290);

	//create an image placeholder for myLabel
	//fill the top left corner with red, just bcuz
	QImage myImage;
	myImage = QImage(320, 240, QImage::Format_RGB888);
	QRgb red = qRgb(255,0,0);
	for(int i=0;i<80;i++) {
		for(int j=0;j<60;j++) {
			myImage.setPixel(i, j, red);
		}
	}

	//create a label, and set it's image to the placeholder
	MyLabel myLabel(myWidget);
	myLabel.setGeometry(10, 10, 320, 240);
	myLabel.setPixmap(QPixmap::fromImage(myImage));

	//create a FFC button
	QPushButton *button1 = new QPushButton("Perform FFC", myWidget);
	button1->setGeometry(320/2-50, 290-35, 100, 30);

	//create a thread to gather SPI data
	//when the thread emits updateImage, the label should update its image accordingly
	LeptonThread *thread = new LeptonThread();
	thread->setLogLevel(loglevel);
	thread->useColormap(typeColormap);
	thread->useLepton(typeLepton);
	thread->useSpiSpeedMhz(spiSpeed);
	// thread->setAutomaticScalingRange();
	// if (0 <= rangeMin) thread->useRangeMinValue(rangeMin);
	// if (0 <= rangeMax) thread->useRangeMaxValue(rangeMax);
	rangeMin = 27315;
	rangeMax = 31092;
	thread->useRangeMinValue(rangeMin);
	thread->useRangeMaxValue(rangeMax);
	QObject::connect(thread, SIGNAL(updateImage(QImage)), &myLabel, SLOT(setImage(QImage)));
	
	//connect ffc button to the thread's ffc action
	QObject::connect(button1, SIGNAL(clicked()), thread, SLOT(performFFC()));
	thread->start();

	QTimer captureTimer;
    captureTimer.setInterval(2000);
	int frameCounter = 0;

	QObject::connect(&captureTimer, &QTimer::timeout, [&]() {
        // capture the frame
        QImage capturedImage = myLabel.pixmap()->toImage();  // Assuming myLabel has a valid pixmap

		 //web application
		//sendImageToServer(capturedImage);

        // save the captured frame as a .tiff file
        QString fileName = QString("/home/remote/FireDetection/rawframes/Sample_Capture_%1.tiff").arg(frameCounter++);
		QString liveFileName = QString("/home/remote/FireDetection/rawframes/Live_Capture.tiff");
        capturedImage.save(fileName, "TIFF");
		capturedImage.save(liveFileName, "TIFF");
		system("python3 /home/remote/FireDetection/LeptonModule/software/raspberrypi_video/dewarp/liveDewarp.py &");
    });
	//web app
	//QWebView webView;
   // webView.load(QUrl("http://10.0.0.151/index.html"));   webView.show();

   QTimer repaintTimer;
	repaintTimer.setInterval(1000); // Adjust the interval as needed
	QObject::connect(&repaintTimer, &QTimer::timeout, [&]() {
    	myLabel.update(); // Force repaint of the label widget
	});
	repaintTimer.start();

	captureTimer.start();

	thread->performFFC();
	
	myWidget->show();

	return a.exec();
}
