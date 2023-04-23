#!/usr/bin/python3
# -*- coding: UTF-8 -*
import PayUtil as payUtil
import AesUtil as aesUtil
import json
import requests

class encoder(json.JSONEncoder):
    def default(self, obj):
        # if isinstance(obj, np.ndarray):
        #     return obj.tolist()
        if isinstance(obj, bytes):
            return str(obj, encoding='utf-8')
        return json.JSONEncoder.default(self, obj)

class channelgateway(object):
    def __init__(self,data,transCode):
        #print(data.keys())
        self.aeskey = data['aesk']
        #print(self.aeskey)
        self.aes = aesUtil.EncryptDate(self.aeskey)
        self.plat_pubk = data.get('plat_pubk')
        self.merch_prik = data.get('mer_prikey')
        self.url = data.get('url')
        self.data = data.get('data')
        self.target = data.get('target')
        self.transCode = transCode
        self.struct = {"cusUid":"3001002","reqSn":"test","transCode":"MB2001","version":"1"}
        self.headers = {'Content-Type': 'application/json'}
        
    #加密
    def encrypt(self,data):
        # 转换为json 字符串
        param = json.dumps(data, cls=encoder)
        print('请求参数:', param)
        # aes 进行加密
        boby = self.aes.encrypt(param)
        print('发送http报文:', boby)
        return boby
    #解密
    def decrypt(self,data):
        decrypt_body = self.aes.decrypt(data)
        print('解密：',decrypt_body)
        return decrypt_body

    #加签
    def sign(self,data):
        # 参数拼接
        str_param = payUtil.getSign(data)
        # rsa 签名
        #print('self.merch_prik:',self.merch_prik)
        sign = payUtil.rsa_sign(str_param,self.merch_prik)
        return sign
    
    #验签
    def signVerify(self,data,sign):
        sign_verify = payUtil.rsa_verify(data,sign,self.plat_pubk)
        print(sign_verify)
        return sign_verify

    #渠道查询内部路由
    def router(self):
        if self.target == 'tigerBusinessOrderBuy':
            return self.tigerBusinessOrderBuy(self.url,self.data,self.struct)
        elif self.target == 'tigerBusinessOrderSell':
            return self.tigerBusinessOrderSell(self.url,self.data,self.struct)
        elif self.target == 'tigerAccountStatus':
            return self.tigerAccountStatus(self.url,self.data,self.struct)
        elif self.target == 'updateStatu':
            return self.updateStatu(self.url,self.data,self.struct)
        elif self.target == 'merchOrderCheck':
            #transCode = 'MB2001'
            return self.merchOrderCheck(self.url,self.data,self.struct,self.transCode)
    
    #通用
    def helper(self,url,data,struct,transCode,):
        #加密
        data_encrypted = self.encrypt(data)
        struct['data'] = data_encrypted
        struct['transCode'] = transCode
        #加签
        signMsg =self.sign(struct)
        #print('signMsg:',signMsg)
        #print(type(signMsg)) 
        struct['signMsg'] = signMsg
        #print('struct:',struct)
        json_struct =json.dumps(struct,cls=encoder)
        headers = {'Content-Type': 'application/json'}
        res = requests.request("POST", url, headers=headers, data=json_struct)
        #print("MB2001")
        print(res.text)
        responseText= res.text
        
        responseText_json =eval(responseText) 
        #print('data:',responseText_json['data'])
        #print(type(responseText_json['data']))
        decrypt_response = self.decrypt(responseText_json['data'])
        print('decrypt_response:',decrypt_response)
        return decrypt_response
    
    #商户购买交易查询
    def merchOrderCheck(self,url,data,struct,transCode):
        res = self.helper(url,data,struct,transCode)
        return res
    #Tiger购买订单商家交易查询        
    def tigerBusinessOrderBuy(self,url,data,struct):
        #加密
        data_encrypted = self.encrypt(data)

        struct['data'] = data_encrypted
        struct['transCode'] = 'MB2001'
        #加签
        signMsg =self.sign(struct)
        print('signMsg:',signMsg)
        print(type(signMsg)) 
        struct['signMsg'] = signMsg
        print('struct:',struct)
        json_struct =json.dumps(struct,cls=encoder)
        headers = {'Content-Type': 'application/json'}
        res = requests.request("POST", url, headers=headers, data=json_struct)
        print("Tiger购买订单商家交易查询")
        responseText= res.text
        return responseText

    #Tiger出售订单商家交易查询        
    def tigerBusinessOrderSell(self,url,data,struct):
        #加密
        data_encrypted = self.encrypt(data)

        struct['data'] = data_encrypted
        print('data_encrypted:',data_encrypted)
        print(type(data_encrypted))
        struct['transCode'] = 'CB2002'
        print('struct:',struct)
        #加签
        signMsg =self.sign(struct) 
        struct['signMsg'] = signMsg
        print('struct:',struct)
        json_struct =json.dumps(struct,cls=encoder)
        headers = {'Content-Type': 'application/json'}
        res = requests.request("POST", url, headers=headers, data=json_struct)
        print("Tiger出售订单商家交易查询") 
        responseText= res.text
        
        return responseText

    #Tiger商家账户查询
    def tigerAccountStatus(self,data,struct):
        req={
        'allianceUid' : self.data['self.data'],
        'channelUid' : self.data['channelUid'],
        'businessUid' : self.data['businessUid'],
        }
        req_encrypt_data = self.encrypt(req)
        req_json={
            'data':req_encrypt_data,
            #TO BE DONE
        }
        response = requests.post(url=self.url,json=req_json)

    #Tiger商家上下线变更  
    def updateStatu(self,data,struct):
        req={
        'allianceUid' : self.data['self.data'],
        'channelUid' : self.data['channelUid'],
        'businessUid' : self.data['businessUid'],
        'bizerStatus' : self.data['bizerStatus']
        }
        req_encrypt_data = self.encrypt(req)
        req_json={
            'data':req_encrypt_data,
            #TO BE DONE
        }
        response = requests.post(url=self.url,json=req_json)

if __name__ == '__main__':
    
    params = {
        #'target' : 'tigerBusinessOrderBuy',
        'target' : 'merchOrderCheck',

        # Tiger出售订单商家交易查询 
        # 'url' : 'http://gateway.jeegc.com/channel/channelOutNotify/queryTransOrder',
        # Tiger购买订单商家交易查询
        #'url' : 'http://gateway.jeegc.com/channel/channelOutNotify/queryTradeOrder',
        'url' : 'http://gateway.jeegc.com/merchant/api',
        # Tiger商家账户查询
        #'url' : '',
        # Tiger商家上下线变更
        #'url' : '',

        'aesk' : 'iTiAatlaRm2UTpMdSZIexg==',
        #平台公钥
        'plat_pubK' : 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtfo/Z3vnz1U1rwGnVL6g9wy1PpowjRkV/sMDWKh9wThXwn2+vJvNSISnUQghwEChpHTn1nuT7Y8QEWo5CSpnpXudA7CRyVv2rdkPBkRUYM1u8Ho76bJppBoW8texe+wveCkXfne8QgbCMGwqPlGhOqP0qvm3f80QFpqEKNZCfYAWKgbthz0XTW/s2HX/JwBr6GqV2vGbTBucAW9gqVhRg3rhYjhpNY+vYnzMeIxXOU8V2EF9P9YJqArsYIg47ORpMQuCk7HPh771a5xLstlYoZ2jALUxHtCavXC9sR+VWPwqoKN21kN+ZpC72+Ycre5GOrZpoJW+0LYms+Ssr+IBPwIDAQAB',
        #plat_pubK = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnv4aQXskLgOIvcBieVauCbNsLuh+261IRilOs/H8R25kSS4fCrvjY6hFJIhanS4FOkHoVh+o+7LyZy89irygOcZUyMAwy08CSZVtusXmXaFw95LSvMN3Heb+hGXxLoJMTd/ZNsTThI/X1m6460ntS4eXoXMNCrVSxHtB6T8+dyq1OPGqdsp3YvHJQjY+ouTeXsOivdWoZfozHzkZD/6cvBcqaIIcaWrVCdoVanqfbNYpeaZEUD9Q/FExuunThmEZeFIXSqvol8k3+rhXNikJ1hQ3lC87GBDvn2jYnjdsh8rjR4SFB1SMZlEZbkA/mPrBxfZJPd4aNXB03z0orTqfRwIDAQAB",
        #商户私钥
        'mer_prikey' : 'MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC1+j9ne+fPVTWvAadUvqD3DLU+mjCNGRX+wwNYqH3BOFfCfb68m81IhKdRCCHAQKGkdOfWe5PtjxARajkJKmele50DsJHJW/at2Q8GRFRgzW7wejvpsmmkGhby17F77C94KRd+d7xCBsIwbCo+UaE6o/Sq+bd/zRAWmoQo1kJ9gBYqBu2HPRdNb+zYdf8nAGvoapXa8ZtMG5wBb2CpWFGDeuFiOGk1j69ifMx4jFc5TxXYQX0/1gmoCuxgiDjs5GkxC4KTsc+HvvVrnEuy2VihnaMAtTEe0Jq9cL2xH5VY/Cqgo3bWQ35mkLvb5hyt7kY6tmmglb7Qtiaz5Kyv4gE/AgMBAAECggEAE5NqAq3Xj/wwnDTnVTx0gF8DmEpp8qPCM/eygnUNoh13g1qXjB6OhMCQZy0ixFWvjcttrSr6DNIY/maY4B2JrMmRaHY0GJ8l+Cmjbh8nnIo85u2fSFKC/r43vcPqOdR8fsac2mPzAn9LoH3iRXXujCpbBZF7ZeofUu8oTGRQHsPcK1G99DiAjmQf4g3bz82NTR3KzH5pMwT7NbMAN5bEEBi/JMbUwNcoV1igy53RSHa+ldu6ykJfRd1SVxAnHy6q4IclX/tjfuAifvTm2lg5DNKrmglaWym4hpNsVpxArLs6l3/+U73gNmipPv41XMJ20BtbsiEpud1eS0FO0BPJoQKBgQDc7ESBLhUs0N60MkV6bh1aaNIHsfN8c25REuYx33C7v1wxfW5i4DkdV1q48898b9MSMIDOKU+WqfirUK0+08YiDVR/RbHmAa0TNZ58k+E+f998D0y0heVuiQ632wb7FVBOVCOg5XmfSOHOKMB29Zowmurqr3ptxNJ3sgD8uIVC1wKBgQDS3vz8Ep8QXSs/QGFBDIAdPUAaK0XPx4f0oS78lYHHVkhmoh8DE8MHKvrapRsWi+XvTHPljnVBF1KqD/uUFdubVw8uns11GQB6Bz5OYsLRZagPGLxacf1Ec0b5MtDNpX/f+eeMmY9D+wKICeFLjvBjF+iyqzYMKVXFNS0uNZRP2QKBgQDDLcnoBvqWOYJH2RIg9B/ivDCys7jV/nU8E2JkNW+3r3yYDKT1nftXvNFeDakF2xWzQD7L5Rt3lHspf4FPvHGTrAs21jAxcNGj4v8+OLgLK5YaWLn/0zu7yELElDE6qr3kNdm0UIh+/TjhlodTkfDDeFqLNLUJPZZkQVM18x9oyQKBgERJb/WVditPcJzYFWaCTM6rMiIHV2E1BWMD+3pSVCegWmvaHl7ZvHOKyJeblg0UGs8GnBV/r5r3mY53BIptFaPVapY3WOONyCi8RcIOm3ZCDE1vPjev6EuNZTN38ERYTvPSMtjGNa3XEHfLc0kLre75JCMP7L29eQgW812efjvpAoGBAIx+/AM/00SzCVi4XUIs5iKXx5SsVJA3du/+IfqQZ3waD+HYSKsf4wL5GLNZW+IMKO2U+57ByuTB1sgfvWyXv7d/VQa4TNwg2tCYXw/ivA8aP4cPisairn/kQoUFeqP/BZsNW6ZZlQBfwo+FgC+iQ/4vzxx0PoHsoOdlQH1DA6Os',
        #Tiger订单商家交易查询 
        # 'data' : {
        #     'allianceUid' : '100',
        #     'channelUid' : '200',
        #     'businessUid' : '300',
        #     'tigerOrderFlowNo' : '20211006400' 
        #     }

        #Tiger商家账户查询
        # 'data' : {
        #     'allianceUid' : '100',
        #     'channelUid' : '200',
        #     'businessUid' : '300'
        #     }
        #Tiger商家上下线变更
        #  'data' : {
        #     'allianceUid' : '100',
        #     'channelUid' : '200',
        #     'businessUid' : '300',
        #     'bizerStatus' : '200'
        #     }
        #商户购买交易查询
        'data' : {
            'merchUID' : 1001001,
            'allianceUid' : 100,
            'channelUid' : 50019,
            'businessUid' : 'cs100',
            'merchOrderNo' : '110651',
            'tigerTradeDate':'20211007'
            }
        }
    transCode = 'MS2001' # MS2001
    a = channelgateway(params,transCode)
    res = a.router()
    #print('res:',res)
    #1
