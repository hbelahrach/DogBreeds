//
//  ViewController.swift
//  Created by mac on 14/04/2018.
//  Copyright © 2018 mac. All rights reserved.
//

import UIKit
import AVFoundation
import Photos
import Material
import Alamofire

class ViewController: UIViewController, UINavigationControllerDelegate, UIImagePickerControllerDelegate {
    let galleryPicker = UIImagePickerController()
    @IBOutlet var preview: UIImageView!
    @IBOutlet var photoBtn: FABButton!
    @IBOutlet var cameraBtn: FABButton!
    @IBOutlet var textLbl: UILabel!
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view, typically from a nib.
        self.photoBtn.setImage(Icon.photoLibrary, for: .normal)
        self.cameraBtn.setImage(Icon.photoCamera, for: .normal)
        self.preview.layer.borderWidth = 2
        self.preview.layer.cornerRadius = 10
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    @IBAction func photoBtnPressed(_ sender: Any) {
        galleryPicker.sourceType = .photoLibrary
        galleryPicker.delegate = self
        present(galleryPicker, animated: true)
    }
    
    
    @IBAction func cameraBtnPressed(_ sender: Any) {
        // Make sure device has a camera
        if UIImagePickerController.isSourceTypeAvailable(.camera) {
            // Setup and present default Camera View Controller
            let imagePicker = UIImagePickerController()
            imagePicker.delegate = self
            imagePicker.sourceType = .camera
            imagePicker.allowsEditing = false
            self.present(imagePicker, animated: true, completion: nil)
        }
    }
    
    func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
        dismiss(animated: true)
        print("canceled")
    }
    
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [String : Any]) {
        if let image = info[UIImagePickerControllerOriginalImage] as? UIImage {
            self.preview.image = image
            self.textLbl.text = "Uploading ......"
            
            Alamofire.upload(multipartFormData: { formData in
                formData.append(UIImagePNGRepresentation(image)!, withName: "image", fileName: "image.jpg", mimeType: "image/jpeg")
            }, to: "http://127.0.0.1:5000/predict", encodingCompletion: { result in
                switch result {
                case .success(let upload, _, _):
                    upload.validate().responseJSON(completionHandler: { response in
                        switch response.result {
                        case .success(let value):
                            let data = value as! [String:Any]
                            self.textLbl.text = "The dog breed is : \(data["prediction"]!)"
                        case .failure((let error)): print("response error \(error)")
                        }
                    })
                case .failure(let error):
                    print("encoding error \(error)")
                }
            })
        }
        dismiss(animated: true)
    }    
}

