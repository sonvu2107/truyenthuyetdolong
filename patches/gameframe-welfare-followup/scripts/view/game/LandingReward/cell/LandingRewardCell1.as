package view.game.LandingReward.cell
{
   import CommonUI.Button.Button1;
   import CommonUI.Label.Label;
   import CommonUI.List.CustomList0;
   import CommonUI.Panel.Panel9;
   import CommonUI.Resources.SkinMgr;
   import CommonUI.baseUI.list.CustomListItemRender;
   import animation.uiEffect.SyncGlowFilterEffect;
   import assets.AssetManager;
   import common.Data.GameData;
   import common.Data.Welfare.user.WelFaceDayInfo;
   import common.Data.achieve.std.StdAchieve;
   import common.Data.achieve.user.UserAchieve;
   import common.GameResource;
   import control.controler.AchieveCC;
   import events.AchieveEvent;
   import events.DataEventDispatcher;
   import events.OtherEvent;
   import flash.display.Bitmap;
   import flash.events.MouseEvent;
   import lang.LangManager;
   import model.UIHelpIdType;
   import utils.TextUtils;
   import view.game.LandingReward.LandingRewardWin;
   import view.game.components.line.Line0;
   import view.game.firstRecharge.FirstAwardGrid;
   import view.game.welfare.page.WellFareLandingRewardPage;

   public class LandingRewardCell1 extends CustomListItemRender
   {


      private var _quanQinID:int = -1;

      private var _labelA:Label;

      private var _rewardGrid:FirstAwardGrid;

      private var _labelB:Label;

      private var _achieveImg:Bitmap;

      private var _line:Line0;

      public var acceptBtn:Button1;

      private var _cellBgArray:Array;

      private var _vIx:int = 440;

      private var _btnEffect1:SyncGlowFilterEffect;

      public function LandingRewardCell1(param1:CustomList0)
      {
         var _loc4_:Bitmap = null;
         super(param1);
         this._quanQinID = int((GameData.welfareProvider.data.LoginachieveID[GameData.welfareProvider.data.LoginachieveID.length - 1] as WelFaceDayInfo).id);
         var _loc2_:Panel9 = new Panel9(SkinMgr.WinBg1);
         _loc2_.setSize(700,70);
         addChild(_loc2_);
         this._labelA = new Label();
         this._labelA.x = 5;
         this._labelA.y = 25;
         this.addChild(this._labelA);
         this._cellBgArray = new Array();
         var _loc3_:int = 0;
         while(_loc3_ < 8)
         {
            _loc4_ = new Bitmap(AssetManager.shopItemBox1.bitmapData);
            this._cellBgArray[_loc3_] = _loc4_;
            addChild(this._cellBgArray[_loc3_]);
            this._cellBgArray[_loc3_].visible = false;
            _loc3_++;
         }
         this._rewardGrid = new FirstAwardGrid();
         this._rewardGrid.x = this._labelA.y + 115;
         this._rewardGrid.y = 10;
         this.addChild(this._rewardGrid);
         this._labelB = new Label();
         this._labelB.x = this._rewardGrid.x + this._vIx + 14;
         this._labelB.y = 25;
         this.addChild(this._labelB);
         this._achieveImg = GameResource.defaultResource.getLangOtherGroupImage(14);
         this._achieveImg.x = this._rewardGrid.x + this._vIx + 20;
         this._achieveImg.y = 10;
         this.addChild(this._achieveImg);
         this.acceptBtn = new Button1();
         this.acceptBtn.setSpaces(17,2,17,3);
         this.acceptBtn.caption = "<font size=\'14\'color=\'#f3f328\'><b>" + LangManager.Lang.landingReward[1] + "</b></font>";
         this.acceptBtn.move(this._rewardGrid.x + this._vIx,20);
         addChild(this.acceptBtn);
         this._btnEffect1 = new SyncGlowFilterEffect(this.acceptBtn);
         this._btnEffect1.stop();
      }

      override public function set data(param1:Object) : void
      {
         var param1:Object = param1;
         var data:UserAchieve = null;
         var str:String = null;
         var day:int = 0;
         var str1:String = null;
         var newData:Object = param1;
         this.clear();
         m_Data = newData;
         if(m_Data)
         {
            data = newData as UserAchieve;
            if(data.stdAchieve.id == this._quanQinID)
            {
               this._rewardGrid.x = this._labelA.y + 100 + 390;
               this.onChangeLoginCounsForWeek(null);
            }
            else
            {
               str = LangManager.Lang.landingReward[6].toString().replace("$value$",data.stdAchieve.name);
               TextUtils.labSetCaption(this._labelA,str,[15326098,13411969],16724787,18,"Tahoma");
               this._labelA.visible = true;
            }
            this._rewardGrid.cellWidth = 48;
            this._rewardGrid.cellHeight = 48;
            this._rewardGrid.gridSpaceWidth = 15;
            this._rewardGrid.gridSpaceHeight = 0;
            this._rewardGrid.colCount = data.stdAchieve.awards.length;
            this._rewardGrid.rowCount = 1;
            this._rewardGrid.setSize(this._rewardGrid.colCount * (this._rewardGrid.gridSpaceWidth + this._rewardGrid.cellWidth),this._rewardGrid.rowCount * (this._rewardGrid.gridSpaceHeight + this._rewardGrid.cellHeight));
            this.setAwardsData(data);
            if(data.hasGetAwards)
            {
               this._achieveImg.visible = true;
            }
            else if(data.hasDone && (data.stdAchieve.id == this._quanQinID || this.conversion(data.stdAchieve.name) <= int(GameData.welfareProvider.data.loginCounsForWeek)))
            {
               this.acceptBtn.helpId = UIHelpIdType.WIN_WELFARE_LOGIN_REWARD_ACCEPT;
               this.acceptBtn.visible = true;
               this.acceptBtn.enabled = true;
               this._btnEffect1.start();
               this.acceptBtn.addEventListener(MouseEvent.CLICK,this.onDarwBtnHandler);
               DataEventDispatcher.addEventListener(AchieveEvent.ACHIEVE_AWARDS_GOT,this.onAchieveHandler);
            }
            else
            {
               day = Math.max(1,this.conversion(data.stdAchieve.name) - int(GameData.welfareProvider.data.loginCounsForWeek));
               this._labelB.visible = true;
               str1 = LangManager.Lang.landingReward[2].toString().replace("$value$",day);
               TextUtils.labSetCaption(this._labelB,str1,[15326098,13411969],16724787,18,"Tahoma");
            }
            if(data.stdAchieve.id == this._quanQinID)
            {
               this._labelB.visible = false;
            }
            DataEventDispatcher.addEventListener(OtherEvent.LOGIN_COUNS_FOR_WEEK,this.onChangeLoginCounsForWeek);
         }
      }

      private function onChangeLoginCounsForWeek(param1:OtherEvent) : void
      {
         var _loc2_:String = null;
         if(data.stdAchieve.id == this._quanQinID)
         {
            _loc2_ = LangManager.Lang.landingReward[5].toString().replace("$value$",int(GameData.welfareProvider.data.loginCounsForWeek));
            TextUtils.labSetCaption(this._labelA,_loc2_,[15326098,13411969],16724787,18,"Tahoma");
            this._labelA.visible = true;
         }
      }

      private function onDarwBtnHandler(param1:MouseEvent) : void
      {
         if(m_Data.stdAchieve.id != this._quanQinID && this.conversion(m_Data.stdAchieve.name) > int(GameData.welfareProvider.data.loginCounsForWeek))
         {
            return;
         }
         AchieveCC.sendGetAwards(m_Data.stdAchieve.id);
      }

      private function setAwardsData(param1:UserAchieve) : void
      {
         var _loc6_:Bitmap = null;
         var _loc2_:StdAchieve = param1.stdAchieve;
         var _loc3_:int = int(_loc2_.awards.length);
         this._rewardGrid.colCount = _loc3_;
         var _loc4_:int = this._rewardGrid.cellWidth * _loc3_ + this._rewardGrid.gridSpaceWidth * (_loc3_ - 1);
         this._rewardGrid.setSize(_loc4_,48);
         var _loc5_:int = 0;
         while(_loc5_ < _loc3_)
         {
            this._rewardGrid.setData(_loc5_,param1.stdAchieve.awards[_loc5_]);
            _loc6_ = this._cellBgArray[_loc5_] as Bitmap;
            _loc6_.x = this._rewardGrid.x + _loc5_ * this._rewardGrid.cellWidth + _loc5_ * this._rewardGrid.gridSpaceWidth - 1;
            --this._rewardGrid.y;
            _loc6_.visible = false;
            _loc5_++;
         }
      }

      private function onAchieveHandler(param1:AchieveEvent) : void
      {
         var _loc2_:UserAchieve = param1.userAchieve;
         if(data.hasDone && _loc2_.stdAchieve.id == data.stdAchieve.id)
         {
            this.acceptBtn.visible = false;
            this.acceptBtn.enabled = false;
            this._btnEffect1.stop();
            this._achieveImg.visible = true;
            LandingRewardWin.isAllAchieve();
            this.acceptBtn.removeEventListener(MouseEvent.CLICK,this.onDarwBtnHandler);
            DataEventDispatcher.removeEventListener(AchieveEvent.ACHIEVE_AWARDS_GOT,this.onAchieveHandler);
         }
      }

      private function conversion(param1:String) : int
      {
         switch(param1)
         {
            case "1":
               return 1;
            case "2":
               return 2;
            case "3":
               return 3;
            case "4":
               return 4;
            case "5":
               return 5;
            case "6":
               return 6;
            case "7":
               return 7;
            default:
               return 0;
         }
      }

      private function clear() : void
      {
         this._achieveImg.visible = false;
         this._labelA.caption = "";
         this._labelA.visible = false;
         this._rewardGrid.clear();
         this.acceptBtn.visible = false;
         this.acceptBtn.enabled = false;
         this._btnEffect1.stop();
         this.acceptBtn.removeEventListener(MouseEvent.CLICK,this.onDarwBtnHandler);
         DataEventDispatcher.removeEventListener(AchieveEvent.ACHIEVE_AWARDS_GOT,this.onAchieveHandler);
         this._labelB.caption = "";
         this._labelB.visible = false;
      }
   }
}
