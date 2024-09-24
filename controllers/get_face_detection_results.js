const AWS = require('aws-sdk');
const rekognition = new AWS.Rekognition();

exports.handler = async (event) => {
    const jobId = event.jobId;  // Pass jobId as input from the event

    try {
        // Check the status of the job using `getFaceDetection`
        const jobId = '2e06bde9b09be025358a9534e7034fcfa1fc5de6ac789fb19e5014228803c2d9'
        const statusResponse = await rekognition.getFaceDetection({ JobId: jobId }).promise();
        console.log('statusResponse => ', statusResponse)

        // Check job status
        const jobStatus = statusResponse.JobStatus;

        if (jobStatus === 'SUCCEEDED') {
            // Job succeeded, return the results
            const faceDetails = statusResponse.Faces;
            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: 'Face detection completed successfully',
                    faces: faceDetails
                }),
            };
        } else if (jobStatus === 'IN_PROGRESS') {
            // Job is still running
            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: 'Face detection is still in progress',
                }),
            };
        } else {
            // Job failed or other status
            return {
                statusCode: 500,
                body: JSON.stringify({
                    message: `Face detection job failed with status: ${jobStatus}`,
                }),
            };
        }
    } catch (error) {
        console.error('Error retrieving face detection status:', error);
        return {
            statusCode: 500,
            body: JSON.stringify({
                message: 'Failed to retrieve face detection status',
                error: error.message,
            }),
        };
    }
};
