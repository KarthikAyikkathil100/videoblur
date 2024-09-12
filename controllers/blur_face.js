const ffmpegPath = require('@ffmpeg-installer/ffmpeg').path;
const ffprobePath = require('@ffprobe-installer/ffprobe').path;
const ffmpeg = require('fluent-ffmpeg');
ffmpeg.setFfmpegPath(ffmpegPath);
ffmpeg.setFfprobePath(ffprobePath)
const { PassThrough } = require('stream');
const tmp = require('tmp');
const fs = require('fs');
const util = require('util');
const S3AWS = require('@aws-sdk/client-s3')
const rekognitionAWS = require('@aws-sdk/client-rekognition');
const s3 = new S3AWS.S3()
const rekognition = new rekognitionAWS.Rekognition();


const downloadFile = async (bucket, key) => {
    // const pass = new PassThrough();
    const response = await s3.getObject({ Bucket: bucket, Key: key });
    return response.Body.pipe(res);
};

const uploadFile = async (bucket, key, filePath) => {
    const fileStream = fs.createReadStream(filePath);
    await s3.upload({ Bucket: bucket, Key: key, Body: fileStream }).promise();
};

const processVideo = async (videoStream, facesData, outputPath) => {
    console.log('processVideo started')
    return new Promise((resolve, reject) => {
        // Create temporary files for input and output
        tmp.file({ postfix: '.mp4' }, (err, tempInputPath, tempInputFd, cleanupCallback) => {
            if (err) return reject(err);

            tmp.file({ postfix: '.mp4' }, (err, tempOutputPath, tempOutputFd, cleanupCallback) => {
                if (err) return reject(err);

                // Save the video stream to a temporary file
                const writeStream = fs.createWriteStream(tempInputPath);
                videoStream.pipe(writeStream);

                writeStream.on('finish', () => {
                    // FFmpeg command to blur faces
                    const ffmpegCommand = ffmpeg(tempInputPath);

                    // Add each face as a filter
                    facesData.forEach(face => {
                        console.log('face => ', face)
                        const { BoundingBox } = face.Face;
                        const { Width, Height, Left, Top } = BoundingBox;
                        const x = Math.round(Left * 100);
                        const y = Math.round(Top * 100);
                        const w = Math.round(Width * 100);
                        const h = Math.round(Height * 100);
                        ffmpegCommand.videoFilters({
                            filter: 'boxblur',
                            options: `10:1:0:0:${x}:${y}:${w}:${h}`
                        });
                    });

                    ffmpegCommand
                        .output(tempOutputPath)
                        .on('end', () => {
                            // Clean up and resolve
                            cleanupCallback();
                            resolve(tempOutputPath);
                        })
                        .on('error', (err) => {
                            reject(err);
                        })
                        .run();
                });
            });
        });
    });
};

const processVideoV2 = async (videoStream, facesData, outputPath) => {
    console.log('processVideo started');
    
    return new Promise((resolve, reject) => {
        tmp.file({ postfix: '.mp4' }, (err, tempInputPath, tempInputFd, tempInputCleanupCallback) => {
            if (err) return reject(err);

            tmp.file({ postfix: '.mp4' }, (err, tempOutputPath, tempOutputFd, tempOutputCleanupCallback) => {
                if (err) {
                    tempInputCleanupCallback();
                    return reject(err);
                }

                // Save the video stream to a temporary file
                const writeStream = fs.createWriteStream(tempInputPath);
                videoStream.pipe(writeStream);

                writeStream.on('finish', () => {
                    // FFmpeg command to blur faces
                    let ffmpegCommand = ffmpeg(tempInputPath);

                    // Accumulate filters
                    const filters = facesData.map(face => {
                        const { BoundingBox } = face.Face;
                        const { Width, Height, Left, Top } = BoundingBox;
                        const x = Math.round(Left * 100);
                        const y = Math.round(Top * 100);
                        const w = Math.round(Width * 100);
                        const h = Math.round(Height * 100);
                        return `boxblur=10:1:0:0:${x}:${y}:${w}:${h}`;
                    });
                    console.log('Here ---- => ', filters)

                    // Apply all filters at once
                    const signleFilter = '\'boxblur=10:1:0:0:56:9:16:16\'';
                    ffmpegCommand.videoFilters(signleFilter);

                    ffmpegCommand
                        .output(tempOutputPath)
                        .on('end', () => {
                            // Clean up temporary files
                            tempInputCleanupCallback();
                            tempOutputCleanupCallback();
                            resolve(tempOutputPath);
                        })
                        .on('error', (err) => {
                            // Clean up temporary files on error
                            tempInputCleanupCallback();
                            tempOutputCleanupCallback();
                            reject(err);
                        })
                        .run();
                });

                writeStream.on('error', (err) => {
                    tempInputCleanupCallback();
                    reject(err);
                });
            });
        });
    });
};

const processVideoV3 = async (videoStream, facesData, outputPath) => {
    console.log('processVideo started');
    
    return new Promise((resolve, reject) => {
        tmp.file({ postfix: '.mp4' }, (err, tempInputPath, tempInputFd, tempInputCleanupCallback) => {
            if (err) return reject(err);

            tmp.file({ postfix: '.mp4' }, (err, tempOutputPath, tempOutputFd, tempOutputCleanupCallback) => {
                if (err) {
                    tempInputCleanupCallback();
                    return reject(err);
                }

                // Save the video stream to a temporary file
                const writeStream = fs.createWriteStream(tempInputPath);
                videoStream.pipe(writeStream);

                writeStream.on('finish', () => {
                    // Get video dimensions
                    ffmpeg.ffprobe(tempInputPath, (err, metadata) => {
                        if (err) {
                            tempInputCleanupCallback();
                            tempOutputCleanupCallback();
                            return reject(err);
                        }

                        const videoWidth = metadata.streams[0].width;
                        const videoHeight = metadata.streams[0].height;
                        console.log('videoWidth => ', videoWidth)
                        console.log('videoHeight => ', videoHeight)
                        // Accumulate filters
                        const filters = facesData.map(face => {
                            const { BoundingBox } = face.Face;
                            const { Width, Height, Left, Top } = BoundingBox;

                            // Convert normalized values to pixel values
                            const x = Math.round(Left * videoWidth);
                            const y = Math.round(Top * videoHeight);
                            const w = Math.round(Width * videoWidth);
                            const h = Math.round(Height * videoHeight);

                            return `boxblur=10:1:0:0:${x}:${y}:${w}:${h}`;
                        }).join(',');

                        // Apply the filters to the video
                        let ffmpegCommand = ffmpeg(tempInputPath).videoFilters(filters);

                        ffmpegCommand
                            .output(tempOutputPath)
                            .on('end', () => {
                                // Clean up temporary files
                                tempInputCleanupCallback();
                                tempOutputCleanupCallback();
                                resolve(tempOutputPath);
                            })
                            .on('error', (err) => {
                                // Clean up temporary files on error
                                tempInputCleanupCallback();
                                tempOutputCleanupCallback();
                                reject(err);
                            })
                            .run();
                    });
                });

                writeStream.on('error', (err) => {
                    tempInputCleanupCallback();
                    reject(err);
                });
            });
        });
    });
};


exports.handler = async (event) => {
    try {
        const bucket = 'project-videostore';  // Replace with your bucket name
        const inputKey = 'potrait_sample.mp4';  // Replace with your input video key
        const outputKey = 'new_potrait_sample.mp4';  // Replace with your output video key

        // Download the video from S3
        console.log('Video download start')
        const videoStream = (await downloadFile(bucket, inputKey));
        console.log('Video download end => ', videoStream)

        // Fetch face detection results
        const jobId = '5e69dd3ba11ff88022dc19ed6f925bec2214bca26d529487765ab9c763acd9bb'
        const response = await rekognition.getFaceDetection({ JobId: jobId }).promise();
        console.log('response from face detection => ', response);
        const facesData = response.Faces;

        // Process the video
        const tempOutputPath = await processVideoV3(videoStream, facesData);

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
