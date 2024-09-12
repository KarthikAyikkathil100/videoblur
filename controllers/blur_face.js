const AWS = require('aws-sdk');
const cv = require('opencv4nodejs');
const { PassThrough } = require('stream');
const s3 = new AWS.S3();
const rekognition = new AWS.Rekognition();
const tmp = require('tmp');
const fs = require('fs');
const util = require('util');

const downloadFile = async (bucket, key) => {
    const pass = new PassThrough();
    await s3
        .getObject({ Bucket: bucket, Key: key })
        .createReadStream()
        .pipe(pass)
    return pass;
};

const uploadFile = async (bucket, key, filePath) => {
    const fileStream = fs.createReadStream(filePath);
    await s3.upload({ Bucket: bucket, Key: key, Body: fileStream }).promise();
};

const blurFaces = async (videoStream, facesData, outputPath) => {
    return new Promise((resolve, reject) => {
        tmp.file({ postfix: '.mp4' }, (err, tempFilePath, fd, cleanupCallback) => {
            if (err) return reject(err);

            const videoWriter = new cv.VideoWriter(tempFilePath, cv.VideoWriter.fourcc('mp4v'), 30, new cv.Size(640, 480));

            const inputVideo = cv.VideoCapture(videoStream);
            let frame;

            while (inputVideo.read(frame)) {
                facesData.forEach(face => {
                    const { BoundingBox } = face;
                    const { Width, Height, Left, Top } = BoundingBox;
                    const x = Math.round(Left * frame.cols);
                    const y = Math.round(Top * frame.rows);
                    const w = Math.round(Width * frame.cols);
                    const h = Math.round(Height * frame.rows);
                    const faceRegion = frame.getRegion(new cv.Rect(x, y, w, h));
                    const blurredFace = faceRegion.gaussianBlur(new cv.Size(99, 99));
                    frame.setRegion(new cv.Rect(x, y, w, h), blurredFace);
                });

                videoWriter.write(frame);
            }

            videoWriter.release();

            // Clean up and resolve
            cleanupCallback();
            resolve(tempFilePath);
        });
    });
};

exports.handler = async (event) => {
    try {
        const bucket = 'project-videostore';  // Replace with your bucket name
        const inputKey = 'potrait_sample.mp4';  // Replace with your input video key
        const outputKey = 'new_potrait_sample.mp4';  // Replace with your output video key

        // Download the video from S3
        const videoStream = await downloadFile(bucket, inputKey);

        // Fetch face detection results
        const jobId = '5e69dd3ba11ff88022dc19ed6f925bec2214bca26d529487765ab9c763acd9bb'
        const response = await rekognition.getFaceDetection({ JobId: jobId }).promise();
        const facesData = response.Faces;

        // Process the video
        const tempOutputPath = await blurFaces(videoStream, facesData);

        // Upload the processed video to S3
        await uploadFile(bucket, outputKey, tempOutputPath);

        // Clean up temporary files
        fs.unlinkSync(tempOutputPath);

        return {
            statusCode: 200,
            body: 'Video processing completed successfully!',
        };
    } catch (error) {
        console.error('Error processing video:', error);
        return {
            statusCode: 500,
            body: `Error processing video: ${error.message}`,
        };
    }
};
