package view.game.welfare.page
{
   import CommonUI.Button.Button0;
   import CommonUI.Label.Label;
   import CommonUI.Panel.Panel7;
   import CommonUI.Resources.SkinMgr;
   import CommonUI.baseUI.events.RichTextLinkEvent;
   import assets.AssetManager;
   import common.AchieveDataMgr;
   import common.Data.GameData;
   import common.Data.achieve.std.StdAchieve;
   import common.Data.achieve.user.UserAchieve;
   import common.GameConst;
   import common.GlobalData;
   import control.navigator.GameNavigateType;
   import control.navigator.GameNavigator;
   import events.DataEventDispatcher;
   import events.OtherEvent;
   import events.PropertyEvent;
   import flash.events.MouseEvent;
   import flash.text.TextFieldAutoSize;
   import lang.LangManager;
   import utils.FilterUtils;
   import view.game.active.ActiveWin;
   import view.game.components.label.SimpleLinkLabel;
   import view.game.components.label.TitleLabel6;
   import view.game.welfare.WelfareWin;
   import view.game.welfare.components.WelFareOffLinePanel;
   import view.game.welfare.components.WelFareWorldLeaf;

   public class WelFareLineLookPage1 extends WelFareBasePage
   {


      private var _offlinePanel:WelFareOffLinePanel;

      private var _worldLeaf:WelFareWorldLeaf;

      private var _emphasisConcernsPanel:Panel7;

      private var _loginNumPanel:Panel7;

      private var _getYuanBaoPanel:Panel7;

      private var _newPlayerPanel:Panel7;

      private var _loginText:Label;

      private var _getYuanBaoText:Label;

      private var _newPlayerText:Label;

      private var _loginBtn:Button0;

      private var _getYuanBaoBtn:Button0;

      private var _newPlayerBtn:Button0;

      private var _achieveConfig:Vector.<StdAchieve>;

      private var _achieveModel:AchieveDataMgr;

      private var _nextStd:StdAchieve;

      public function WelFareLineLookPage1()
      {
         var _loc3_:SimpleLinkLabel = null;
         var _loc5_:SimpleLinkLabel = null;
         var _loc7_:SimpleLinkLabel = null;
         this._achieveConfig = GameData.achieveProvider.awardAchieveList;
         this._achieveModel = GlobalData.achieveDataMgr;
         this._worldLeaf = new WelFareWorldLeaf();
         this.addChild(this._worldLeaf);
         this._emphasisConcernsPanel = new Panel7(SkinMgr.WinBg1);
         this._emphasisConcernsPanel.setSize(330,145);
         this._emphasisConcernsPanel.move(0,175);
         this._emphasisConcernsPanel.visible = false;
         addChild(this._emphasisConcernsPanel);
         var _loc1_:TitleLabel6 = new TitleLabel6();
         _loc1_.setSize(150,25);
         _loc1_.move(this._emphasisConcernsPanel.uiWidth - _loc1_.uiWidth >> 1,10);
         _loc1_.caption = LangManager.Lang.welfare[61];
         this._emphasisConcernsPanel.addChild(_loc1_);
         var _loc2_:Label = new Label();
         _loc2_.autoSize = TextFieldAutoSize.LEFT;
         _loc2_.setSize(this._emphasisConcernsPanel.uiWidth,20);
         _loc2_.move(40,_loc1_.y + 30);
         _loc2_.caption = LangManager.Lang.welfare[62].toString().replace("$value$",0);
         this._emphasisConcernsPanel.addChild(_loc2_);
         _loc3_ = new SimpleLinkLabel(LangManager.Lang.welfare[66].toString());
         _loc3_.move(this._emphasisConcernsPanel.uiWidth - 5 - 130,_loc2_.y + 2);
         _loc3_.filters = FilterUtils.DefaultTextFilters;
         this._emphasisConcernsPanel.addChild(_loc3_);
         var _loc4_:Label;
         (_loc4_ = new Label()).autoSize = TextFieldAutoSize.LEFT;
         _loc4_.setSize(this._emphasisConcernsPanel.uiWidth,20);
         _loc4_.move(40,_loc2_.y + _loc2_.uiHeight + 5);
         _loc4_.caption = LangManager.Lang.welfare[63].toString().replace("$value$",0);
         this._emphasisConcernsPanel.addChild(_loc4_);
         (_loc5_ = new SimpleLinkLabel(LangManager.Lang.welfare[66].toString())).move(this._emphasisConcernsPanel.uiWidth - 5 - 130,_loc4_.y + 2);
         _loc5_.filters = FilterUtils.DefaultTextFilters;
         this._emphasisConcernsPanel.addChild(_loc5_);
         var _loc6_:Label;
         (_loc6_ = new Label()).autoSize = TextFieldAutoSize.LEFT;
         _loc6_.setSize(this._emphasisConcernsPanel.uiWidth,20);
         _loc6_.move(40,_loc4_.y + _loc4_.uiHeight + 5);
         _loc6_.caption = LangManager.Lang.welfare[64].toString().replace("$value$",0);
         this._emphasisConcernsPanel.addChild(_loc6_);
         (_loc7_ = new SimpleLinkLabel(LangManager.Lang.welfare[66].toString())).move(this._emphasisConcernsPanel.uiWidth - 5 - 130,_loc6_.y + 2);
         _loc7_.filters = FilterUtils.DefaultTextFilters;
         this._emphasisConcernsPanel.addChild(_loc7_);
         var _loc8_:Label;
         (_loc8_ = new Label()).autoSize = TextFieldAutoSize.LEFT;
         _loc8_.setSize(this._emphasisConcernsPanel.uiWidth,20);
         _loc8_.move(40,_loc6_.y + _loc6_.uiHeight + 5);
         _loc8_.caption = LangManager.Lang.welfare[65].toString().replace("$value$",0);
         this._emphasisConcernsPanel.addChild(_loc8_);
         var _loc9_:SimpleLinkLabel;
         (_loc9_ = new SimpleLinkLabel(LangManager.Lang.welfare[66].toString())).move(this._emphasisConcernsPanel.uiWidth - 5 - 130,_loc8_.y + 2);
         _loc9_.filters = FilterUtils.DefaultTextFilters;
         this._emphasisConcernsPanel.addChild(_loc9_);
         _loc3_.linkURL = "1";
         _loc5_.linkURL = "2";
         _loc7_.linkURL = "3";
         _loc9_.linkURL = "4";
         _loc3_.addEventListener(RichTextLinkEvent.LINK,this.onClickEC);
         _loc5_.addEventListener(RichTextLinkEvent.LINK,this.onClickEC);
         _loc7_.addEventListener(RichTextLinkEvent.LINK,this.onClickEC);
         _loc9_.addEventListener(RichTextLinkEvent.LINK,this.onClickEC);
         this._offlinePanel = new WelFareOffLinePanel();
         this._offlinePanel.setSize(360,320);
         this._offlinePanel.title = LangManager.Lang.welfare[17];
         this._offlinePanel.move(340,0);
         addChild(this._offlinePanel);
         this._loginNumPanel = new Panel7(AssetManager.fuLiLineLookBg);
         this._loginNumPanel.setSize(232,77);
         this._loginNumPanel.move(this._emphasisConcernsPanel.x,this._emphasisConcernsPanel.y + this._emphasisConcernsPanel.uiHeight + 5);
         addChild(this._loginNumPanel);
         this._loginText = new Label();
         this._loginText.setSize(230,40);
         this._loginText.autoSize = TextFieldAutoSize.CENTER;
         this._loginText.move(this._loginNumPanel.uiWidth - this._loginText.uiWidth >> 1,5);
         this._loginNumPanel.addChild(this._loginText);
         this._loginBtn = new Button0();
         this._loginBtn.setSpaces(15,2,15,2);
         this._loginBtn.caption = LangManager.Lang.welfare[58];
         this._loginBtn.move(this._loginNumPanel.uiWidth - this._loginBtn.uiWidth >> 1,this._loginNumPanel.uiHeight - 15 - this._loginBtn.uiHeight);
         this._loginNumPanel.addChild(this._loginBtn);
         this._loginBtn.addEventListener(MouseEvent.CLICK,this.onClickLoginBtn);
         this._getYuanBaoPanel = new Panel7(AssetManager.fuLiLineLookBg);
         this._getYuanBaoPanel.setSize(232,77);
         this._getYuanBaoPanel.move(this._loginNumPanel.x + this._loginNumPanel.uiWidth + 5,this._loginNumPanel.y);
         addChild(this._getYuanBaoPanel);
         this._getYuanBaoText = new Label();
         this._getYuanBaoText.setSize(230,40);
         this._getYuanBaoText.autoSize = TextFieldAutoSize.CENTER;
         this._getYuanBaoText.move(this._getYuanBaoPanel.uiWidth - this._getYuanBaoText.uiWidth >> 1,5);
         this._getYuanBaoText.caption = "";
         this._getYuanBaoPanel.addChild(this._getYuanBaoText);
         this._getYuanBaoBtn = new Button0();
         this._getYuanBaoBtn.setSpaces(15,2,15,2);
         this._getYuanBaoBtn.caption = LangManager.Lang.welfare[59];
         this._getYuanBaoBtn.move(this._getYuanBaoPanel.uiWidth - this._getYuanBaoBtn.uiWidth >> 1,this._getYuanBaoPanel.uiHeight - 15 - this._getYuanBaoBtn.uiHeight);
         this._getYuanBaoPanel.addChild(this._getYuanBaoBtn);
         this._getYuanBaoBtn.addEventListener(MouseEvent.CLICK,this.onClickGetYuanBaoBtn);
         this._newPlayerPanel = new Panel7(AssetManager.fuLiLineLookBg);
         this._newPlayerPanel.setSize(232,77);
         this._newPlayerPanel.move(this._getYuanBaoPanel.x + this._getYuanBaoPanel.uiWidth + 5,this._getYuanBaoPanel.y);
         addChild(this._newPlayerPanel);
         this._newPlayerText = new Label();
         this._newPlayerText.setSize(230,40);
         this._newPlayerText.autoSize = TextFieldAutoSize.CENTER;
         this._newPlayerText.move(this._newPlayerPanel.uiWidth - this._newPlayerText.uiWidth >> 1,5);
         this._newPlayerText.caption = LangManager.Lang.welfare[57];
         this._newPlayerPanel.addChild(this._newPlayerText);
         this._newPlayerBtn = new Button0();
         this._newPlayerBtn.setSpaces(15,2,15,2);
         this._newPlayerBtn.caption = LangManager.Lang.welfare[60];
         this._newPlayerBtn.move(this._newPlayerPanel.uiWidth - this._newPlayerBtn.uiWidth >> 1,this._newPlayerPanel.uiHeight - 15 - this._newPlayerBtn.uiHeight);
         this._newPlayerPanel.addChild(this._newPlayerBtn);
         this._newPlayerBtn.addEventListener(MouseEvent.CLICK,this.onClickNewPlayerBtn);
         this.nextNoAchieve();
         this.onChangeLoginCouns(null);
         this.discrepancy(null);
         super();
      }

      private function onClickLoginBtn(param1:MouseEvent) : void
      {
         (GameNavigator.getWinByType(GameNavigateType.WIN_WelFare) as WelfareWin).setWinTabIndex(WelfareWin.DENG_LU_JIANG_LI);
      }

      private function onClickGetYuanBaoBtn(param1:MouseEvent) : void
      {
         (GameNavigator.getWinByType(GameNavigateType.WIN_WelFare) as WelfareWin).setWinTabIndex(WelfareWin.CHONG_ZHI_JING_XI);
      }

      private function onClickNewPlayerBtn(param1:MouseEvent) : void
      {
         (GameNavigator.getWinByType(GameNavigateType.WIN_WelFare) as WelfareWin).setWinTabIndex(WelfareWin.LI_BAO_FENG_SHANG);
      }

      private function onChangeLoginCouns(param1:OtherEvent) : void
      {
         if(this._loginText != null)
         {
            this._loginText.caption = LangManager.Lang.welfare[55].toString().replace("$value$",GameData.welfareProvider.data.loginCouns);
         }
      }

      override protected function initData() : void
      {
      }

      override protected function upDateLayout() : void
      {
      }

      override public function initEvent() : void
      {
         DataEventDispatcher.addEventListener(PropertyEvent.MAIN_MONEY_CHANGE,this.onPropertyChange);
         this._offlinePanel.initEvent();
         this._worldLeaf.inEvent();
         this.onPropertyChange(null);
         this.nextNoAchieve();
         DataEventDispatcher.addEventListener(OtherEvent.LOGIN_COUNS,this.onChangeLoginCouns);
      }

      override public function removeEvent() : void
      {
         this._offlinePanel.removeEvent();
         this._worldLeaf.removeEvent();
         DataEventDispatcher.removeEventListener(PropertyEvent.MAIN_MONEY_CHANGE,this.onPropertyChange);
      }

      private function onPropertyChange(param1:PropertyEvent) : void
      {
         if(this._nextStd)
         {
            this.discrepancy(this._nextStd);
         }
      }

      private function discrepancy(param1:StdAchieve) : void
      {
         var _loc3_:String = null;
         if(!param1)
         {
            return;
         }
         var _loc2_:int = param1.nextAim - GlobalData.role.drawYBCount;
         if(_loc2_ <= 0)
         {
            _loc2_ = 0;
         }
         _loc3_ = _loc2_ >= 1000000000?(Math.round(_loc2_ / 100000000) / 10).toString().replace(".0","") + "B":_loc2_ >= 1000000?(Math.round(_loc2_ / 100000) / 10).toString().replace(".0","") + "M":_loc2_ >= 1000?(Math.round(_loc2_ / 100) / 10).toString().replace(".0","") + "K":_loc2_.toString();
         this._getYuanBaoText.caption = LangManager.Lang.welfare[56].toString().replace("$value$",_loc3_);
      }

      private function nextNoAchieve() : void
      {
         var _loc3_:StdAchieve = null;
         var _loc4_:UserAchieve = null;
         var _loc5_:int = 0;
         var _loc6_:String = null;
         if(!GlobalData.achieveDataMgr.hasInit())
         {
            return;
         }
         var _loc1_:int = this._achieveConfig.length;
         var _loc2_:int = 0;
         while(_loc2_ < _loc1_)
         {
            _loc3_ = this._achieveConfig[_loc2_];
            if(!(_loc4_ = this._achieveModel.getUserAchieveAt(_loc3_.id)).stdAchieve.isDelete)
            {
               if(!_loc4_.hasDone && !_loc4_.hasGetAwards)
               {
                  if(_loc3_.id == GameConst.FIRST_AWARD_GIFE)
                  {
                     if((_loc5_ = _loc3_.nowAim - GlobalData.role.drawYBCount) <= 0)
                     {
                        _loc5_ = 0;
                     }
                     _loc6_ = _loc5_ >= 1000000000?(Math.round(_loc5_ / 100000000) / 10).toString().replace(".0","") + "B":_loc5_ >= 1000000?(Math.round(_loc5_ / 100000) / 10).toString().replace(".0","") + "M":_loc5_ >= 1000?(Math.round(_loc5_ / 100) / 10).toString().replace(".0","") + "K":_loc5_.toString();
                     this._getYuanBaoText.caption = LangManager.Lang.welfare[56].toString().replace("$value$",_loc6_);
                  }
                  else if(_loc2_ != 0)
                  {
                     this._nextStd = this._achieveConfig[_loc2_ - 1];
                  }
                  return;
               }
            }
            _loc2_++;
         }
         this._getYuanBaoText.caption = LangManager.Lang.welfare[56].toString().replace("$value$",0);
      }

      private function onClickEC(param1:RichTextLinkEvent) : void
      {
         var _loc2_:int = int(param1.linkURL);
         var _loc3_:ActiveWin = GameNavigator.showWin(GameNavigateType.WIN_Active) as ActiveWin;
         _loc3_.setWinTabIndex(_loc2_);
      }

      override public function set visible(param1:Boolean) : void
      {
         super.visible = param1;
         if(param1)
         {
            if(GameNavigator.getWinByType(GameNavigateType.WIN_WelFare) as WelfareWin != null)
            {
               (GameNavigator.getWinByType(GameNavigateType.WIN_WelFare) as WelfareWin).setWinSize(0);
            }
         }
      }
   }
}
