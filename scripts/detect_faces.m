#import <AppKit/AppKit.h>
#import <Foundation/Foundation.h>
#import <Vision/Vision.h>

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        if (argc != 2) {
            fprintf(stderr, "usage: detect_faces IMAGE\n");
            return 2;
        }

        NSString *path = [NSString stringWithUTF8String:argv[1]];
        NSImage *image = [[NSImage alloc] initWithContentsOfFile:path];
        NSData *tiff = [image TIFFRepresentation];
        NSBitmapImageRep *bitmap = [[NSBitmapImageRep alloc] initWithData:tiff];
        CGImageRef cgImage = [bitmap CGImage];
        if (!cgImage) {
            fprintf(stderr, "unable to open image\n");
            return 3;
        }

        VNDetectFaceRectanglesRequest *request = [[VNDetectFaceRectanglesRequest alloc] init];
        VNImageRequestHandler *handler = [[VNImageRequestHandler alloc] initWithCGImage:cgImage options:@{}];
        NSError *error = nil;
        if (![handler performRequests:@[request] error:&error]) {
            fprintf(stderr, "face detection failed: %s\n", error.localizedDescription.UTF8String);
            return 4;
        }

        CGFloat width = CGImageGetWidth(cgImage);
        CGFloat height = CGImageGetHeight(cgImage);
        NSArray<VNFaceObservation *> *faces = [request.results sortedArrayUsingComparator:^NSComparisonResult(VNFaceObservation *a, VNFaceObservation *b) {
            CGFloat ay = (1.0 - a.boundingBox.origin.y - a.boundingBox.size.height) * height;
            CGFloat by = (1.0 - b.boundingBox.origin.y - b.boundingBox.size.height) * height;
            if (fabs(ay - by) > 25.0) return ay < by ? NSOrderedAscending : NSOrderedDescending;
            return a.boundingBox.origin.x < b.boundingBox.origin.x ? NSOrderedAscending : NSOrderedDescending;
        }];

        NSInteger index = 0;
        for (VNFaceObservation *face in faces) {
            CGRect box = face.boundingBox;
            CGFloat x = box.origin.x * width;
            CGFloat y = (1.0 - box.origin.y - box.size.height) * height;
            CGFloat w = box.size.width * width;
            CGFloat h = box.size.height * height;
            printf("%ld,%.2f,%.2f,%.2f,%.2f,%.4f\n", (long)index, x, y, w, h, face.confidence);
            index++;
        }
    }
    return 0;
}
